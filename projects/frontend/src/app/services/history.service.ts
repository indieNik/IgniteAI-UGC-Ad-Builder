import { inject, Injectable } from '@angular/core';
import { Firestore, collection, collectionData, query, where, orderBy, limit } from '@angular/fire/firestore';
import { AuthService } from './auth.service';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';
import { HistoryCacheService } from './history-cache.service';

export interface RunStatus {
    run_id: string;
    status: string;
    timestamp: number;
    request?: any;
    result?: any;
    output_url?: string;
    project_name?: string;
    created_at?: number;
    updated_at?: number;
    scene_results?: any;
}

@Injectable({
    providedIn: 'root'
})
export class HistoryService {
    private historySubject = new BehaviorSubject<RunStatus[]>([]);
    public history$ = this.historySubject.asObservable();

    private selectedRunSubject = new BehaviorSubject<RunStatus | null>(null);
    public selectedRun$ = this.selectedRunSubject.asObservable();

    private loadSubscription: Subscription | undefined;
    private firestore: Firestore = inject(Firestore);
    private auth: AuthService = inject(AuthService);
    private cacheService: HistoryCacheService = inject(HistoryCacheService);
    private currentUserId: string | null = null;

    constructor() {
        // Subscribe to user changes
        this.auth.user$.subscribe(user => {
            if (user) {
                this.currentUserId = user.uid;
                this.loadHistoryWithCache(user.uid);
            } else {
                this.currentUserId = null;
                this.historySubject.next([]);
            }
        });
    }

    loadHistoryWithCache(userId: string) {
        // Try cache first
        const cached = this.cacheService.getCache(userId);
        if (cached) {
            this.historySubject.next(cached);
            // Still listen for real-time updates in background
            this.listenToHistory(userId);
        } else {
            // No cache, load from Firestore
            this.listenToHistory(userId);
        }
    }

    listenToHistory(userId: string) {
        if (this.loadSubscription) {
            this.loadSubscription.unsubscribe();
        }

        const historyQuery = query(
            collection(this.firestore, 'executions'),
            where('user_id', '==', userId),
            orderBy('updated_at', 'desc'),
            limit(20)
        );

        this.loadSubscription = collectionData(historyQuery, { idField: 'run_id' }).subscribe((runs: any[]) => {
            this.historySubject.next(runs);
            // Update cache
            this.cacheService.setCache(userId, runs);
        });
    }

    refreshHistory() {
        // Force refresh by clearing cache
        this.cacheService.clearCache();
        if (this.currentUserId) {
            this.listenToHistory(this.currentUserId);
        }
    }

    invalidateCacheForRun(runId: string) {
        // Called when a run is regenerated
        this.cacheService.invalidateOnRegeneration(runId);
    }

    selectRun(run: RunStatus) {
        this.selectedRunSubject.next(run);
    }
}
