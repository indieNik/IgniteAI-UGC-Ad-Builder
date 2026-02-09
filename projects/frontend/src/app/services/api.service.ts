import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface GenerateResponse {
    run_id: string;
    status: string;
    message: string;
}

export interface GenerateRequest {
    prompt: string;
    product_image_path?: string;
    config?: any;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private apiUrl = `${environment.apiUrl}/api`;

    get baseUrl(): string {
        return environment.apiUrl;
    }

    constructor(private http: HttpClient) { }

    triggerGeneration(prompt: string, imagePath?: string, config?: any): Observable<GenerateResponse> {
        const payload: GenerateRequest = {
            prompt: prompt,
            product_image_path: imagePath,
            config: config
        };
        return this.http.post<GenerateResponse>(`${this.apiUrl}/generate`, payload);
    }

    uploadImage(file: File): Observable<{ path: string, filename: string, run_id: string }> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<{ path: string, filename: string, run_id: string }>(`${this.apiUrl}/upload`, formData);
    }

    checkHealth(): Observable<any> {
        return this.http.get<{ status: string }>(`${this.apiUrl.replace('/api', '')}/health`);
    }

    checkStatus(runId: string): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/status/${runId}`);
    }

    getHistory(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/history`);
    }

    getLogStream(runId: string, token: string): string {
        // Dynamic WS URL based on apiUrl
        let wsUrl = this.apiUrl.replace('http', 'ws').replace('https', 'wss');
        // Append Firebase token as query parameter for WebSocket authentication
        return `${wsUrl}/ws/logs/${runId}?token=${encodeURIComponent(token)}`;
    }

    downloadRun(runId: string): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/download/${runId}`, { responseType: 'blob' });
    }

    getBrand(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/brand`);
    }

    updateBrand(config: any): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/brand`, config);
    }

    regenerateScene(runId: string, sceneId: string, prompt?: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/regenerate-scene/${runId}/${sceneId}`, { prompt });
    }

    preFlightCheck(inputData: string, imagePath?: string): Observable<PreFlightResult> {
        console.log('🔍 [FE DEBUG] Pre-flight check called', {
            inputDataLength: inputData?.length,
            imagePath
        });
        return this.http.post<PreFlightResult>(`${this.apiUrl}/pre-flight-check`, {
            input_data: inputData,
            image_path: imagePath
        });
    }
}

export interface PreFlightResult {
    safe_to_proceed: boolean;
    requires_confirmation: boolean;
    warnings: PreFlightWarning[];
    has_person_detected: boolean;
}

export interface PreFlightWarning {
    code: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    recommendation: string;
}


