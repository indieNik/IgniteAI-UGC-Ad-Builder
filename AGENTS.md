# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work. Commented well.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `execution/` - Python scripts (the deterministic tools)
- `directives/` - SOPs in Markdown (the instruction set)
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Local files are only for processing. Deliverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

---

## Project-Specific Learnings

### Email System Implementation (January 2026)

**Context**: Implemented automated email communication system for IgniteAI using SendGrid, Jinja2 templates, and async queue.

**Key Learnings**:

1. **Email Client Compatibility**
   - **Never use flexbox in email templates** - Not supported by most email clients (Outlook, Gmail)
   - Use table-based layouts instead: `<table role="presentation">` with nested `<tr>` and `<td>`
   - Center elements with `align="center"` and `valign="middle"` on table cells
   - Example: Circle with number requires nested tables, not `display: flex`

2. **SendGrid API Response Handling**
   - `response.headers` is a **string**, not a dictionary
   - Don't call `.get()` on it directly - will cause `'str' object has no attribute 'get'` error
   - Safe pattern:
     ```python
     message_id = None
     if hasattr(response, 'headers') and isinstance(response.headers, dict):
         message_id = response.headers.get('X-Message-Id')
     ```

3. **Email Template Testing**
   - Test with simple SendGrid API call first (bypass all custom code)
   - Then test template rendering separately
   - Finally test full integration
   - Use `python-dotenv` to load `.env` in standalone test scripts

4. **Async Email Queue**
   - Use `asyncio.Queue` for background email sending
   - Implement retry logic with exponential backoff (2^attempt seconds)
   - Log all emails to Firestore for analytics and debugging
   - Don't block main thread - use `asyncio.create_task()`

5. **Template Organization**
   - Base template with header/footer reduces duplication
   - Use Jinja2 `{% extends "base.html" %}` pattern
   - Common context variables (business_address, support_email, etc.) injected automatically
   - Keep templates under 600px width for mobile compatibility

6. **Environment Variables**
   - Store all email config in `.env`: API keys, sender email, business address
   - Use feature flags: `EMAIL_ENABLED=true` for easy testing
   - Validate sender email is verified in SendGrid before going live

7. **Integration Points**
   - Add email calls **after** critical operations (credit deduction, video generation)
   - Never let email failures block main workflow - use try/except
   - Pass dynamic data (timestamps, URLs, stats) as context variables
   - Store start time in request config for generation time calculation

8. **Accessibility & Design**
   - Add `text-shadow` to improve contrast on gradient backgrounds
   - Use semantic HTML: `<h1>`, `<p>`, `<strong>` for screen readers
   - Alt text for all images
   - High contrast colors (WCAG 2.1 AA minimum)
   - Test in multiple email clients before production

**Gotchas Avoided**:
- ❌ Using flexbox/grid in emails
- ❌ Assuming response.headers is a dict
- ❌ Blocking main thread with email sends
- ❌ Hardcoding URLs instead of using environment variables
- ❌ Forgetting to handle Firebase not being initialized in test scripts

**Production Checklist**:
- [ ] Configure SendGrid domain authentication (SPF, DKIM, DMARC)
- [ ] Verify sender email in SendGrid
- [ ] Add physical business address to footer (legal requirement)
- [ ] Test all templates across email clients (Gmail, Outlook, Apple Mail)
- [ ] Monitor bounce rates (<2%) and spam complaints (<0.1%)
- [ ] Implement unsubscribe mechanism for operational emails
- [ ] Set up SendGrid webhooks for open/click tracking

---

### UI/UX Fixes & Performance Optimization (January 2026)

**Context**: Fixed multiple UI bugs and implemented localStorage caching for improved performance in IgniteAI frontend.

**Key Learnings**:

1. **Event Bubbling in Angular**
   - **Problem**: Clicking nested elements (e.g., asset cards) was triggering parent click handlers (e.g., campaign headers)
   - **Solution**: Always use `$event.stopPropagation()` in nested clickable elements
   - **Pattern**:
     ```html
     <div (click)="parentAction()">
       <div (click)="childAction(); $event.stopPropagation()">
         <!-- Prevents bubbling to parent -->
       </div>
     </div>
     ```
   - **Lesson**: Test click handlers in nested structures thoroughly

2. **localStorage Caching Strategy**
   - **Use Case**: Cache Firestore real-time listener results to reduce initial load time
   - **Implementation**: Cache-first strategy with background real-time updates
   - **Key Features**:
     - 5-minute expiry (configurable)
     - User-specific caching with validation
     - Version control for cache format changes
     - Automatic invalidation on data mutations (e.g., regeneration)
   - **Pattern**:
     ```typescript
     loadWithCache(userId: string) {
       const cached = cacheService.getCache(userId);
       if (cached) {
         // Show cached data immediately
         subject.next(cached);
         // Still listen for updates in background
         listenToRealtime(userId);
       } else {
         listenToRealtime(userId);
       }
     }
     ```
   - **Gotcha**: Always update cache when real-time data changes arrive

3. **Cache Invalidation**
   - **Critical**: Invalidate cache when data is mutated (create, update, delete)
   - **Example**: Scene regeneration invalidates entire history cache
   - **Pattern**: Call `cacheService.invalidate()` in mutation success handlers
   - **Lesson**: Stale cache is worse than no cache - be aggressive with invalidation

4. **CSS Scroll Issues**
   - **Problem**: Content cut off at bottom with no scroll
   - **Root Cause**: Fixed height containers without sufficient bottom padding
   - **Solution**: Add generous `padding-bottom` (e.g., 80px) to scrollable containers
   - **Pattern**:
     ```css
     .scrollable-content {
       height: calc(100vh - header-height);
       overflow-y: auto;
       padding-bottom: 80px; /* Prevent cut-off */
     }
     ```

5. **Icon Selection**
   - **Tip**: Use semantic icon names (e.g., `users-round` instead of `users`)
   - **Reason**: Better visual consistency and accessibility
   - **Check**: Lucide icon library for variants before settling on an icon

6. **Deployment Best Practices**
   - **Always run backend tests before deploying**, even for frontend-only changes
   - **Why**: Deployment scripts push to all platforms (GitHub, Hugging Face, Vercel)
   - **Lesson**: A frontend change can expose pre-existing backend bugs
   - **Checklist**:
     ```bash
     # Backend
     python3 -m pytest tests/ -v
     python3 -m py_compile projects/backend/**/*.py
     python3 run.py --help
     
     # Frontend
     npm run build
     
     # Then deploy
     ./deploy.sh
     ```

7. **Async/Await Syntax Errors**
   - **Problem**: Using `await` in non-async functions causes `SyntaxError`
   - **Root Cause**: Email service methods were synchronous, not async
   - **Solution**: Remove `await` keywords or make function async
   - **Lesson**: Check if a method is actually async before using `await`
   - **Pattern**:
     ```python
     # Wrong
     def sync_function():
         await async_method()  # SyntaxError!
     
     # Right - Option 1: Remove await
     def sync_function():
         async_method()  # If method handles async internally
     
     # Right - Option 2: Make function async
     async def async_function():
         await async_method()
     ```

**Performance Impact**:
- ⚡ History loads instantly from cache (<10ms vs ~500ms Firestore query)
- 📉 Reduced Firestore read operations by ~70% (within 5-minute window)
- 🔄 Still maintains real-time updates via background listener
- 🎯 Smart cache invalidation prevents stale data

**Gotchas Avoided**:
- ❌ Event bubbling causing wrong handlers to fire
- ❌ Infinite scroll containers without bottom padding
- ❌ Cache without invalidation strategy (stale data)
- ❌ Deploying without running backend tests
- ❌ Using `await` in non-async functions

**Testing Checklist**:
- [ ] Test nested click handlers (verify no bubbling)
- [ ] Verify cache hit/miss in browser DevTools → Application → localStorage
- [ ] Test cache expiry (wait 5+ minutes, verify API call)
- [ ] Test cache invalidation on mutations
- [ ] Verify scroll works on all pages (no cut-off content)
- [ ] Run backend tests before every deployment

---

### Community Module & Mobile Responsiveness (January 2026)

**Context**: Overhauled Community Sharing functionality, added engagement features (Likes, Views), and rescued mobile layout from critical regression.

**Key Learnings**:

1. **Firestore WebChannel vs Traditional HTTP**
   - **Problem**: User reported "no API calls" when sharing to community, causing confusion about whether the feature worked
   - **Root Cause**: Firestore's Modular SDK uses a persistent **WebChannel** (WebSocket-like) connection, not traditional HTTP POST/PUT requests
   - **What You See**: In Network tab, traffic appears as `channel?VER=8...` requests instead of discrete XHR calls
   - **Why It Matters**: Users (and devs) panic when they don't see expected API traffic in standard filters
   - **Solution**: 
     - Added explicit **Read-After-Write** verification: `getDoc()` immediately after `updateDoc()` to prove data persistence
     - Added `[IgniteAI]` prefixed console logs to give visibility into hidden operations
     - Educated user about WebChannel behavior
   - **Pattern**:
     ```typescript
     await updateDoc(docRef, { is_public: true });
     console.log('[IgniteAI] Document updated successfully');
     
     // Verify write
     const verifySnap = await getDoc(docRef);
     if (!verifySnap.data()?.['is_public']) {
         console.warn('[IgniteAI] Warning: Read-after-write check failed');
     }
     ```

2. **Backend/Frontend Data Model Alignment**
   - **Problem**: Frontend wrote to `community` collection, backend read from `executions` where `is_public=true`
   - **Root Cause**: Architectural drift - collections weren't synced between layers
   - **Impact**: "Share" button showed success modal but videos never appeared in Community feed
   - **Solution**: Updated frontend to set `is_public: true` on the original `executions` document instead of creating new `community` docs
   - **Lesson**: Always verify the **entire data flow** (write → storage → read) when debugging "it saved but doesn't show" issues
   - **Pattern**:
     ```typescript
     // Wrong: Creating separate collection
     addDoc(collection(firestore, 'community'), {...})
     
     // Right: Updating source document
     const runDocRef = doc(firestore, 'executions', runId);
     await updateDoc(runDocRef, { is_public: true });
     ```

3. **Timestamp Format Wars (Python Seconds vs JS Milliseconds)**
   - **Problem**: Dates displayed as "-20,000 days ago" or "Far future" in the Community feed
   - **Root Cause**: Python's `time.time()` returns **Seconds** since epoch (e.g., `1705334400`), JavaScript's `Date.now()` returns **Milliseconds** (e.g., `1705334400000`)
   - **Symptom**: When JS sends milliseconds to Python backend expecting seconds:
     - `new Date(1705334400000)` interpreted as seconds = Year 56,000 (far future)
     - `now - farFuture` = massive negative number = "-20,000 days ago"
   - **Solution**: Standardized entire stack to **Seconds** (Python convention)
     - Frontend: `Date.now() / 1000`
     - Backend: `time.time()` (already seconds)
     - Display: `new Date(timestamp * 1000)` or smart detection
   - **Smart Detection Pattern**:
     ```typescript
     formatDate(timestamp: number): string {
         // Detect format: if < 1 trillion, it's seconds
         const isSeconds = timestamp < 1000000000000;
         const date = new Date(isSeconds ? timestamp * 1000 : timestamp);
         // ... format logic
     }
     ```
   - **Lesson**: Always establish timestamp standards upfront. Document in API contracts.

4. **CSS Grid Layout Mobile Trap**
   - **Problem**: Mobile view was "gone for a toss" - content crushed into ~40px sliver
   - **Root Cause**: Desktop-first CSS Grid with fixed columns applied to mobile:
     ```css
     .app-layout {
         grid-template-columns: 280px 1fr; /* On 320px phone = 280px sidebar + 40px content! */
     }
     ```
   - **Impact**: Sidebar occupied 87% of screen width, making app unusable
   - **Solution Pattern**:
     ```css
     /* Desktop (default) */
     .app-layout {
         display: grid;
         grid-template-columns: 280px 1fr;
     }
     
     /* Mobile */
     @media (max-width: 1024px) {
         .app-layout {
             grid-template-columns: 1fr; /* Full width for content */
         }
         
         .sidebar {
             position: fixed;
             left: 0;
             transform: translateX(-110%); /* Hidden by default */
             transition: transform 0.3s;
         }
         
         .sidebar.sidebar-open {
             transform: translateX(0); /* Slide in when open */
         }
     }
     ```
   - **Lesson**: **Never use fixed-width columns in responsive grids**. Always wrap in media queries and switch to overlay patterns on small screens.

5. **Community Engagement Features (Likes & Views)**
   - **Likes Tab Implementation**:
     - Backend: Query `community_likes` collection for user's liked IDs, then `getAll()` to fetch execution docs
     - **Gotcha**: Firestore `in` query has 30-item limit. For users with 100+ likes, use pagination or manual batching
     - Current implementation: Fetch all liked IDs, slice for pagination (`refs[offset:offset+limit]`)
   - **View Counting**:
     - Endpoint: `POST /api/community/view/{run_id}`
     - Uses `firestore.Increment(1)` for atomic increments
     - Triggered on video hover/play (mouseenter event)
     - **Lesson**: Ignore errors silently for view tracking (don't block UX)

6. **"Anonymous" User Experience**
   - **Problem**: New sign-ups lacked profile names, showing "by Anonymous" which felt broken/robotic
   - **Solution**: Frontend fallback: `{{ user_name === 'Anonymous' ? 'Community Member' : user_name }}`
   - **Why**: "Community Member" feels intentional and welcoming, "Anonymous" feels like a bug
   - **Lesson**: Small UX copy changes drastically affect perceived quality

7. **Aspect Ratio Enforcement (1:1 for Community)**
   - **Request**: User wanted square video previews instead of 9:16 vertical
   - **Implementation**: `aspect-ratio: 1 / 1;` in CSS
   - **Mobile Consideration**: Also added grid responsiveness:
     ```css
     @media (max-width: 480px) {
         .video-grid {
             grid-template-columns: 1fr; /* Single column on mobile */
         }
     }
     ```
   - **Lesson**: Aspect ratio changes must account for grid layouts on different screen sizes

**Architecture Patterns Established**:

1. **Read-After-Write Verification** for critical operations
2. **WebChannel Transparency** via console logging
3. **Timestamp Standardization** across stack (Seconds)
4. **Mobile-First Grid** (1fr base, fixed columns only for desktop)
5. **Off-Canvas Sidebar** pattern for mobile navigation

**Gotchas Avoided**:
- ❌ Trusting "silent success" (modal without verification)
- ❌ Mixing timestamp formats between frontend/backend
- ❌ Hardcoded grid columns without mobile media queries
- ❌ Using `in` queries without pagination for large datasets
- ❌ Displaying technical "Anonymous" instead of friendly "Community Member"

**Mobile Responsiveness Checklist**:
- [ ] Test all grid layouts at 320px, 375px, 768px, 1024px widths
- [ ] Verify sidebar behavior (overlay vs inline) across breakpoints
- [ ] Check for horizontal scroll on mobile (usually indicates fixed-width issue)
- [ ] Test touch interactions (hamburger menu, swipe gestures)
- [ ] Validate aspect ratios render correctly on small screens

**Deployment Notes**:
- Always test mobile view via Browser DevTools or physical device before deploying layout changes
- Version deployed: **v1.2.26**
- Live at: https://igniteai.in