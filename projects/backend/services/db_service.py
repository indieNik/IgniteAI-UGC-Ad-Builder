import time
from projects.backend.firebase_setup import get_firestore_client
from google.cloud import firestore


class FirestoreService:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection = self.db.collection('executions')

    def save_run(self, run_id: str, user_id: str, status: str, result: dict = None, request_data: dict = None, cost: float = None, credits_used: int = None, failure_reason: str = None):
        """Creates or updates a run document."""
        doc_ref = self.collection.document(run_id)
        
        data = {
            "run_id": run_id,
            "user_id": user_id,
            "status": status,
            "updated_at": time.time()
        }
        
        if status == "queued":
            data["created_at"] = time.time()
            if request_data:
                data["request"] = request_data
        
        if result:
            data["result"] = result
            
        if cost is not None:
            data["cost_usd"] = cost
            
        if credits_used is not None:
            data["credits_used"] = credits_used

        if failure_reason:
            data["failure_reason"] = failure_reason
            
        doc_ref.set(data, merge=True)


    def get_user_history(self, user_id: str, limit: int = 20):
        """Fetch history for a user."""
        try:
            query = self.collection.where("user_id", "==", user_id).order_by(
                "updated_at", direction=firestore.Query.DESCENDING
            ).limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    def get_run(self, run_id: str):
        doc = self.collection.document(run_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_all_runs(self, limit: int = 50, start_after=None):
        """Admin: Fetch all runs."""
        query = self.collection.order_by(
            "updated_at", direction=firestore.Query.DESCENDING
        ).limit(limit)
        
        if start_after:
            query = query.start_after(start_after)
            
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def get_user_role(self, email: str) -> str:
        """Fetch user role from user_roles collection."""
        try:
            # Try exact match first
            doc = self.db.collection('user_roles').document(email).get()
            if doc.exists:
                return doc.to_dict().get("role", "user")
            
            # Try lowercase match
            if email != email.lower():
                doc = self.db.collection('user_roles').document(email.lower()).get()
                if doc.exists:
                     return doc.to_dict().get("role", "user")

            return "user"
        except Exception:
            return "user"
                     


    def get_margin_stats(self):
        """Calculate platform margins (Revenue vs COGS)."""
        try:
            # Stream optimized projection
            docs = self.collection.select(['cost_usd', 'credits_used', 'status']).stream()
            
            total_cogs = 0.0
            total_credits = 0
            
            for doc in docs:
                data = doc.to_dict()
                
                # COGS
                c = data.get('cost_usd')
                if c:
                    total_cogs += float(c)
                    
                # Credits
                cr = data.get('credits_used')
                if cr:
                    total_credits += int(cr)
                    
            revenue = total_credits * 0.80  # ~$0.80 per credit (avg of USD tiers)
            margin = revenue - total_cogs
            margin_percent = (margin / revenue * 100) if revenue > 0 else 0
            
            return {
                 "revenue": round(revenue, 2),
                 "cogs": round(total_cogs, 2),
                 "margin": round(margin, 2),
                 "margin_percent": round(margin_percent, 1),
                 "credits_consumed": total_credits
            }
        except Exception as e:
            print(f"Error calculating margins: {e}")
            return {"error": str(e)}

    def get_admin_stats(self):
        """
        Aggregate stats for admin dashboard. 
        Note: In high-scale, use distributed counters.
        """
        # 1. Total Runs (Count)
        runs_ref = self.collection
        count_query = runs_ref.count()
        count_res = count_query.get()
        total_runs = count_res[0][0].value
        
        # 2. Total AI Model Spend (Exact Sum Aggregation)
        # We use Firestore's server-side aggregation to sum the 'cost_usd' field.
        # This tracks the $ spend on Gemini/Veo/Imagen/etc.
        total_model_spend = 0.0
        try:
            # Explicitly use firestore_v1 as requested
            from google.cloud.firestore_v1 import aggregation
            aggregate_query = aggregation.AggregationQuery(runs_ref)
            aggregate_query.sum("cost_usd", alias="total_cost")
            results = aggregate_query.get()
            total_model_spend = results[0][0].value or 0.0
        except (ImportError, Exception):
            # Fallback 1: Try Old Method
            try:
                from google.cloud.firestore import Sum
                sum_query = runs_ref.aggregate(Sum("cost_usd"))
                sum_res = sum_query.get()
                total_model_spend = sum_res[0][0].value or 0.0
            except Exception:
                # Fallback 2: Manual Stream (Robust Fallback)
                # print(f"Info: Using manual aggregation fallback.")
                all_docs = runs_ref.select(['cost_usd', 'result.cost_usd']).stream()
                for d in all_docs:
                     d_data = d.to_dict()
                     # Check root
                     c = d_data.get("cost_usd")
                     # Check nested
                     if c is None:
                         c = d_data.get("result", {}).get("cost_usd", 0.0)
                     total_model_spend += float(c or 0.0)

        
        # 3. User Metrics (Now / 7d / 30d)
        # We fetch recent runs to determine activity.
        # Limit 1000 should cover most recent activity even in moderate scale.
        recent_runs = runs_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(1000).stream()
        
        active_now = set()
        active_7d = set()
        active_30d = set()
        
        now = time.time()
        time_15m = now - (15 * 60)
        time_7d = now - (7 * 24 * 60 * 60)
        time_30d = now - (30 * 24 * 60 * 60)
        
        for doc in recent_runs:
            data = doc.to_dict()
            uid = data.get("user_id")
            if not uid: continue
                
            ts = data.get("updated_at", 0)
            
            if ts > time_15m:
                active_now.add(uid)
            if ts > time_7d:
                active_7d.add(uid)
            if ts > time_30d:
                active_30d.add(uid)
                
        return {
            "total_runs": total_runs,
            "total_cost_usd": round(total_model_spend, 4),
            "active_users_now": len(active_now),
            "active_users_7d": len(active_7d),
            "active_users_30d": len(active_30d),
            "sample_size": "All Time"
        }

    def record_payment(self, user_id: str, payment_data: dict):
        """Records a successful payment transaction."""
        payment_id = payment_data.get('razorpay_payment_id')
        if not payment_id:
            return
        
        doc_ref = self.db.collection('payments').document(payment_id)
        payment_data['user_id'] = user_id
        payment_data['timestamp'] = time.time()
        doc_ref.set(payment_data)

    def add_credits(self, user_id: str, amount: int):
        """Adds credits to a user's account."""
        doc_ref = self.db.collection('user_credits').document(user_id)
        # Using atomicity/increment for credits
        doc_ref.set({
            "credits": firestore.Increment(amount),
            "updated_at": time.time()
        }, merge=True)

    def get_credits(self, user_id: str) -> int:
        """Fetch current credit balance. New users start with 0 (credits awarded after email verification)."""
        doc_ref = self.db.collection('user_credits').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("credits", 0)
        
        # NEW USERS START WITH 0 CREDITS
        # Trial credits awarded AFTER email verification (see auth.py)
        doc_ref.set({
            "credits": 0,
            "is_trial": False,
            "awaiting_verification": True,
            "created_at": time.time(),
            "updated_at": time.time()
        })
        return 0



    def deduct_credits(self, user_id: str, amount: int) -> bool:
        """
        Deducts credits from user balance with a safety check.
        Returns True if successful, False if insufficient credits.
        """
        user_ref = self.db.collection('user_credits').document(user_id)
        
        @firestore.transactional
        def update_in_transaction(transaction, user_ref):
            snapshot = user_ref.get(transaction=transaction)
            if not snapshot.exists:
                return False
            
            # Use current credits, defaulting to 0
            current_credits = snapshot.get('credits') or 0
            if current_credits < amount:
                return False
            
            transaction.update(user_ref, {
                'credits': firestore.Increment(-amount),
                'updated_at': time.time()
            })
            return True

        transaction = self.db.transaction()
        try:
            return update_in_transaction(transaction, user_ref)
        except Exception as e:
            print(f"Error deducting credits: {e}")
            return False

    def refund_credits(self, user_id: str, amount: int, reason: str, run_id: str) -> bool:
        """
        Refunds credits to user with idempotency check to prevent double refunds.
        Returns True if refund processed, False if already refunded.
        
        Args:
            user_id: User ID to refund credits to
            amount: Number of credits to refund
            reason: Reason for refund (e.g., "visual_dna: Model not found")
            run_id: Run ID that triggered the refund (used as idempotency key)
        """
        # Check if refund already processed for this run
        refund_doc_id = f"{run_id}_refund"
        refund_ref = self.db.collection('refunds').document(refund_doc_id)
        
        existing_refund = refund_ref.get()
        if existing_refund.exists:
            print(f"Refund already processed for run {run_id}. Skipping.")
            return False
        
        # Process refund with transaction
        user_ref = self.db.collection('user_credits').document(user_id)
        
        @firestore.transactional
        def refund_transaction(transaction, user_ref, refund_ref):
            # Add credits back
            transaction.update(user_ref, {
                'credits': firestore.Increment(amount),
                'updated_at': time.time()
            })
            
            # Record refund for audit trail and idempotency
            transaction.set(refund_ref, {
                'run_id': run_id,
                'user_id': user_id,
                'amount': amount,
                'reason': reason,
                'timestamp': time.time(),
                'refunded_at': time.time()
            })
            
            return True
        
        try:
            transaction = self.db.transaction()
            result = refund_transaction(transaction, user_ref, refund_ref)
            print(f"✅ Refunded {amount} credits to user {user_id} for run {run_id}")
            return result
        except Exception as e:
            print(f"❌ Error processing refund: {e}")
            return False

    def upsert_brand(self, user_id: str, brand_data: dict):
        """Creates or updates brand configuration for a user."""
        doc_ref = self.db.collection('brands').document(user_id)
        brand_data['updated_at'] = time.time()
        doc_ref.set(brand_data, merge=True)
        return brand_data

    def get_brand(self, user_id: str):
        """Fetch brand configuration for a user."""
        doc = self.db.collection('brands').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def track_event(self, user_id: str, event_name: str, metadata: dict = None):
        """Logs a product analytics event."""
        event_ref = self.db.collection('events').document()
        event_data = {
            "user_id": user_id,
            "event_name": event_name,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        event_ref.set(event_data)
        return event_data

    def save_fcm_token(self, user_id: str, token: str):
        """Save FCM token to user document."""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.set({
                'fcmToken': token,
                'fcmTokenUpdatedAt': time.time()
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error saving FCM token: {e}")
            return False

    def get_fcm_token(self, user_id: str):
        """Retrieve FCM token for a user."""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict().get('fcmToken')
            return None
        except Exception as e:
            print(f"Error retrieving FCM token: {e}")
            return None
    
    def get_user_profile(self, user_id: str):
        """Retrieve user profile information (email, name, etc.)."""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error retrieving user profile: {e}")
            return None
    
    def track_event(self, user_id: str, event_name: str, properties: dict = None):
        """Track user events for analytics."""
        try:
            self.db.collection('events').add({
                'user_id': user_id,
                'event_name': event_name,
                'properties': properties or {},
                'timestamp': time.time()
            })
        except Exception as e:
            print(f"Error tracking event: {e}")
    
    # ===== Subscription Management Methods =====
    
    def create_subscription(self, user_id: str, subscription_data: dict):
        """Create a new subscription for a user."""
        try:
            self.db.collection('subscriptions').document(user_id).set(subscription_data, merge=True)
        except Exception as e:
            print(f"Error creating subscription: {e}")
            raise
    
    def get_user_subscription(self, user_id: str):
        """Get user's subscription."""
        try:
            doc = self.db.collection('subscriptions').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    def get_subscription_by_razorpay_id(self, razorpay_subscription_id: str):
        """Get subscription by Razorpay ID."""
        try:
            query = self.db.collection('subscriptions').where(
                "razorpay_subscription_id", "==", razorpay_subscription_id
            ).limit(1)
            
            docs = list(query.stream())
            if docs:
                data = docs[0].to_dict()
                data['user_id'] = docs[0].id  # Add user_id from document ID
                return data
            return None
        except Exception as e:
            print(f"Error getting subscription by Razorpay ID: {e}")
            return None
    
    def update_subscription(self, user_id: str, update_data: dict):
        """Update user's subscription."""
        try:
            self.db.collection('subscriptions').document(user_id).update(update_data)
        except Exception as e:
            print(f"Error updating subscription: {e}")
            raise
    
    def set_credits(self, user_id: str, credits: int):
        """Set user's credit balance (for subscription resets)."""
        try:
            self.db.collection('user_credits').document(user_id).set({
                'credits': credits,
                'updated_at': time.time()
            }, merge=True)
        except Exception as e:
            print(f"Error setting credits: {e}")
            raise


db_service = FirestoreService()
