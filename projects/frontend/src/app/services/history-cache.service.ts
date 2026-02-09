import { Injectable } from '@angular/core';

interface CacheEntry {
    data: any[];
    timestamp: number;
    userId: string;
    version: number;
}

@Injectable({
    providedIn: 'root'
})
export class HistoryCacheService {
    private readonly CACHE_KEY = 'igniteai_history_cache';
    private readonly CACHE_VERSION = 1;
    private readonly CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

    constructor() { }

    /**
     * Get cached history for a user if valid
     */
    getCache(userId: string): any[] | null {
        try {
            const cached = localStorage.getItem(this.CACHE_KEY);
            if (!cached) return null;

            const entry: CacheEntry = JSON.parse(cached);

            // Validate cache
            if (entry.userId !== userId) {
                console.log('[Cache] User mismatch, invalidating');
                this.clearCache();
                return null;
            }

            if (entry.version !== this.CACHE_VERSION) {
                console.log('[Cache] Version mismatch, invalidating');
                this.clearCache();
                return null;
            }

            const age = Date.now() - entry.timestamp;
            if (age > this.CACHE_EXPIRY_MS) {
                console.log(`[Cache] Expired (${Math.round(age / 1000)}s old), invalidating`);
                this.clearCache();
                return null;
            }

            console.log(`[Cache] HIT - ${entry.data.length} runs, ${Math.round(age / 1000)}s old`);
            return entry.data;
        } catch (error) {
            console.error('[Cache] Error reading cache:', error);
            this.clearCache();
            return null;
        }
    }

    /**
     * Store history in cache
     */
    setCache(userId: string, data: any[]): void {
        try {
            const entry: CacheEntry = {
                data,
                timestamp: Date.now(),
                userId,
                version: this.CACHE_VERSION
            };

            localStorage.setItem(this.CACHE_KEY, JSON.stringify(entry));
            console.log(`[Cache] STORED - ${data.length} runs`);
        } catch (error) {
            console.error('[Cache] Error storing cache:', error);
            // Quota exceeded or other error - clear cache
            this.clearCache();
        }
    }

    /**
     * Clear the cache
     */
    clearCache(): void {
        try {
            localStorage.removeItem(this.CACHE_KEY);
            console.log('[Cache] CLEARED');
        } catch (error) {
            console.error('[Cache] Error clearing cache:', error);
        }
    }

    /**
     * Invalidate cache when a run is regenerated
     */
    invalidateOnRegeneration(runId: string): void {
        console.log(`[Cache] Invalidating due to regeneration of ${runId}`);
        this.clearCache();
    }
}
