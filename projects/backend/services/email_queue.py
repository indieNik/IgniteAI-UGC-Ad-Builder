"""
Email Queue Service for IgniteAI
Handles asynchronous email sending with retry logic
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from collections import deque
import json

logger = logging.getLogger(__name__)


class EmailQueue:
    """Asynchronous email queue with retry logic"""
    
    def __init__(self, num_workers: int = 3):
        self.queue = asyncio.Queue()
        self.num_workers = num_workers
        self.workers = []
        self.dead_letter_queue = deque(maxlen=100)  # Store failed emails
        self.running = False
        
    async def enqueue_email(self, email_data: Dict) -> str:
        """
        Add email to queue for async processing
        
        Args:
            email_data: Dictionary containing email parameters
                - to_email: str
                - subject: str
                - template_name: str
                - context: Dict
                - category: str (optional)
                
        Returns:
            str: Job ID for tracking
        """
        job_id = f"email_{datetime.now().timestamp()}"
        email_data['job_id'] = job_id
        email_data['enqueued_at'] = datetime.now().isoformat()
        email_data['retry_count'] = 0
        
        await self.queue.put(email_data)
        logger.info(f"Email enqueued: {job_id} to {email_data.get('to_email')}")
        
        return job_id
    
    async def _worker(self, worker_id: int):
        """Background worker to process email queue"""
        from projects.backend.services.email_service import email_service
        
        logger.info(f"Email worker {worker_id} started")
        
        while self.running:
            try:
                # Get email from queue (with timeout to allow graceful shutdown)
                try:
                    email_data = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                job_id = email_data.get('job_id')
                retry_count = email_data.get('retry_count', 0)
                
                logger.info(f"Worker {worker_id} processing {job_id} (attempt {retry_count + 1})")
                
                # Send email
                success = await email_service.send_email(
                    to_email=email_data['to_email'],
                    subject=email_data['subject'],
                    template_name=email_data['template_name'],
                    context=email_data['context'],
                    category=email_data.get('category', 'transactional')
                )
                
                if success:
                    logger.info(f"Worker {worker_id} completed {job_id}")
                else:
                    # Retry logic
                    if retry_count < 3:
                        email_data['retry_count'] = retry_count + 1
                        # Re-enqueue with exponential backoff
                        await asyncio.sleep(2 ** retry_count)
                        await self.queue.put(email_data)
                        logger.warning(f"Retrying {job_id} (attempt {retry_count + 2})")
                    else:
                        # Move to dead letter queue
                        self.dead_letter_queue.append(email_data)
                        logger.error(f"Email {job_id} failed after 3 retries, moved to DLQ")
                
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                
        logger.info(f"Email worker {worker_id} stopped")
    
    async def start(self):
        """Start email queue workers"""
        if self.running:
            logger.warning("Email queue already running")
            return
            
        self.running = True
        
        # Start worker tasks
        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
            
        logger.info(f"Email queue started with {self.num_workers} workers")
    
    async def stop(self):
        """Stop email queue workers gracefully"""
        if not self.running:
            return
            
        self.running = False
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Wait for queue to empty
        await self.queue.join()
        
        logger.info("Email queue stopped")
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        return {
            "queue_size": self.queue.qsize(),
            "workers": self.num_workers,
            "running": self.running,
            "dead_letter_queue_size": len(self.dead_letter_queue)
        }


# Singleton instance
email_queue = EmailQueue(num_workers=3)
