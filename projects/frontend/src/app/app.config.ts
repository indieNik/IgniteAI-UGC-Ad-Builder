import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './interceptors/auth.interceptor';
import { provideFirebaseApp, initializeApp } from '@angular/fire/app';
import { provideAuth, getAuth } from '@angular/fire/auth';
import { provideFirestore, getFirestore } from '@angular/fire/firestore';
import { provideMessaging, getMessaging } from '@angular/fire/messaging';
import { environment } from '../environments/environment';

import { routes } from './app.routes';
import {
  LucideAngularModule,
  Menu,
  Folder,
  Sparkles,
  Zap,
  ChevronDown,
  ChevronRight,
  Image,
  Shield,
  CircleDollarSign,
  ArrowLeft,
  HelpCircle,
  Settings,
  Upload,
  Plus,
  MoreVertical,
  Eye,
  Terminal,
  Package,
  X,
  Film,
  FolderOpen,
  LogOut,
  AlertCircle,
  Smartphone,
  Monitor,
  BarChart,
  GraduationCap,
  ArrowRight,
  Check,
  Play,
  Download,
  TrendingUp,
  Banknote,
  RefreshCw,
  Briefcase,
  CreditCard,
  Save,
  ShieldCheck,
  Layers,
  Loader
} from 'lucide-angular';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimations(), // Enable Angular animations for @slideDown, @fadeIn, etc.
    provideHttpClient(withInterceptors([authInterceptor])),
    provideFirebaseApp(() => initializeApp(environment.firebase)),
    provideAuth(() => getAuth()),
    provideFirestore(() => getFirestore()),
    provideMessaging(() => getMessaging()),
    importProvidersFrom(LucideAngularModule.pick({
      Menu, Folder, Sparkles, Zap, ChevronDown, ChevronRight, Image, Shield,
      CircleDollarSign, ArrowLeft, HelpCircle, Settings, Upload, Plus,
      MoreVertical, Eye, Terminal, Package, X, Film, FolderOpen, LogOut, AlertCircle,
      Smartphone, Monitor, BarChart, GraduationCap, ArrowRight,
      Check, Play, Download, TrendingUp, Banknote, RefreshCw,
      Briefcase, CreditCard, Save, ShieldCheck, Layers, Loader
    }))
  ]
};

