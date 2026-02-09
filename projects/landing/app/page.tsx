'use client';

import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Zap, Banknote, TrendingUp, Sparkles, Check, Play, ArrowRight, Volume2, VolumeX } from 'lucide-react';
import { auth, googleProvider } from '../lib/firebase';
import { signInWithPopup } from 'firebase/auth';
import { PRODUCT_CONTENT } from '../lib/product-content';
import { useState, useEffect } from 'react';

// Import feature icons mapping
const featureIcons = {
  'zap': Zap,
  'banknote': Banknote,
  'trending-up': TrendingUp,
};

// Map features with icons from imported content
const features = PRODUCT_CONTENT.features.map(feature => ({
  icon: featureIcons[feature.icon as keyof typeof featureIcons],
  title: feature.title,
  desc: feature.description,
}));

// Use pricing from imported content
const pricingPlans = PRODUCT_CONTENT.pricing.plans;

const handleFreeSignup = async () => {
  try {
    // Google Sign-In
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;

    // Call backend to setup free tier
    const response = await fetch('https://igniteai-backend-254654034407.us-central1.run.app/api/auth/free-signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uid: user.uid,
        email: user.email,
        name: user.displayName,
        provider: 'google'
      })
    });

    if (!response.ok) {
      throw new Error('Signup failed');
    }

    const data = await response.json();

    // Redirect to app with token for auto sign-in
    window.location.href = `https://app.igniteai.in?token=${data.customToken}&new=true`;
  } catch (error: any) {
    console.error('Signup failed:', error);
    alert(error.message || 'Signup failed. Please try again.');
  }
};

export default function Home() {
  // Simulation State
  const [simulationStage, setSimulationStage] = useState<'text' | 'loading' | 'video'>('text');
  const [visibleLines, setVisibleLines] = useState<string[]>([]);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    const textSequence = [
      "Analyzing product data...",
      "Identifying viral hooks...",
      "Drafting ad scripts...",
      "Synthesizing voiceover...",
      "Rendering scenes..."
    ];

    let timeouts: NodeJS.Timeout[] = [];

    if (simulationStage === 'text') {
      setVisibleLines([]);

      let cumulativeTime = 0;
      textSequence.forEach((line, index) => {
        cumulativeTime += 1200; // 1200ms per line
        const id = setTimeout(() => {
          setVisibleLines([line]);
        }, cumulativeTime);
        timeouts.push(id);
      });

      // Switch to loading after text sequence
      const switchId = setTimeout(() => {
        setSimulationStage('loading');
      }, cumulativeTime + 1200);
      timeouts.push(switchId);

    } else if (simulationStage === 'loading') {
      // Show loader for 2 seconds then switch to video
      const loadId = setTimeout(() => {
        setSimulationStage('video');
      }, 2000);
      timeouts.push(loadId);

    } else if (simulationStage === 'video') {
      // Loop back to text after video plays
      const resetId = setTimeout(() => {
        setSimulationStage('text');
      }, 8000);
      timeouts.push(resetId);
    }

    return () => timeouts.forEach(clearTimeout);
  }, [simulationStage]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <Navbar />

      {/* Hero Section - REDESIGNED */}
      <section className="relative pt-40 pb-32 px-6 min-h-[90vh] flex items-center overflow-hidden">
        {/* Enhanced ambient effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 -left-64 w-[600px] h-[600px] bg-purple-500/30 rounded-full blur-[150px] animate-pulse" />
          <div className="absolute bottom-1/3 -right-64 w-[600px] h-[600px] bg-indigo-500/30 rounded-full blur-[150px] animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-pink-500/20 rounded-full blur-[120px]" />
        </div>

        <div className="relative max-w-[1400px] mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">

            {/* Hero Content - LEFT (7 cols) */}
            <div className="lg:col-span-7 space-y-10">
              {/* Badge */}
              <div className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full text-sm font-medium bg-gradient-to-r from-purple-500/15 via-pink-500/15 to-indigo-500/15 border border-purple-400/30 text-purple-200 backdrop-blur-xl shadow-lg shadow-purple-500/10">
                <Sparkles className="w-4 h-4 text-purple-300" />
                <span className="font-semibold">Powered by Veo 3 + Imagen 3</span>
              </div>

              {/* Headline */}
              <div className="space-y-10">
                <h1 className="text-6xl lg:text-7xl xl:text-8xl font-black leading-[0.95] tracking-tight">
                  <span className="block text-white">Stop Burning</span>
                  <span className="block text-white">Cash on</span>
                  <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent animate-gradient">
                    Creative Fatigue
                  </span>
                </h1>

                <p className="text-xl sm:text-2xl text-slate-200 leading-relaxed font-light">
                  Generate short-form ad videos designed for <strong className="text-white font-semibold">iteration</strong>, <strong className="text-white font-semibold">testing</strong>, and <strong className="text-white font-semibold">scale</strong>. Create variations without shipping product or hiring actors.
                </p>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <a
                  href="https://app.igniteai.in/sign-in"
                  className="group relative inline-flex items-center justify-center gap-3 px-10 py-5 text-lg font-bold text-white rounded-2xl bg-gradient-to-r from-purple-600 via-purple-500 to-indigo-600 hover:from-purple-500 hover:via-purple-400 hover:to-indigo-500 shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/70 hover:-translate-y-1 transition-all duration-300"
                >
                  <span>Ignite My First Campaign</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </a>
                <a
                  href="#pricing"
                  className="inline-flex items-center justify-center px-10 py-5 text-lg font-semibold text-white rounded-2xl border-2 border-slate-600 hover:border-purple-400 bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300"
                >
                  View Pricing
                </a>
              </div>

              {/* Social proof - ENHANCED */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 pt-8 border-t border-white/5">
                <div className="flex -space-x-4">
                  {[
                    ['from-purple-500', 'to-pink-500'],
                    ['from-blue-500', 'to-cyan-500'],
                    ['from-orange-500', 'to-rose-500'],
                    ['from-emerald-500', 'to-teal-500']
                  ].map((gradient, i) => (
                    <div
                      key={i}
                      className={`w-12 h-12 rounded-full bg-gradient-to-br ${gradient[0]} ${gradient[1]} border-3 border-slate-900 ring-2 ring-slate-800 shadow-xl`}
                    />
                  ))}
                </div>
                <div>
                  <p className="text-slate-200 font-semibold text-lg">Trusted by 500+ D2C Founders</p>
                  <p className="text-slate-500 text-sm italic">Built for teams that iterate on creatives, not generate once.</p>
                </div>
              </div>
            </div>

            {/* Hero Visual - RIGHT (5 cols) - DRAMATICALLY IMPROVED */}
            <div className="lg:col-span-5 flex justify-center lg:justify-end">
              <div className="relative w-full" style={{ maxWidth: '400px' }}>
                {/* Glow effect behind card */}
                <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/30 to-pink-500/30 rounded-3xl blur-3xl" />

                {/* Main card */}
                <div className="relative glass-card p-7 rounded-3xl shadow-2xl border-2 border-white/10">
                  {/* Header */}
                  <div className="flex justify-between items-center mb-6 pb-5 border-b border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-slate-200 text-sm font-bold tracking-wide">generation_v2.mp4</span>
                    </div>
                    <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-400/30 text-purple-200 uppercase tracking-wider">
                      <Sparkles className="w-3.5 h-3.5" />
                      AI Generated
                    </span>
                  </div>

                  {/* Video preview  - MUCH LARGER */}
                  <div className="aspect-[9/16] rounded-2xl bg-slate-950 mb-6 relative overflow-hidden group shadow-2xl">

                    {/* State 1: Terminal Text */}
                    <div className={`absolute inset-0 p-8 flex flex-col justify-center items-center font-mono text-sm transition-opacity duration-500 ${simulationStage === 'text' ? 'opacity-100 z-20' : 'opacity-0 z-0'}`}>
                      <div className="space-y-4 w-full max-w-[240px]">
                        {visibleLines.map((line, i) => (
                          <div key={line} className="text-emerald-400 flex items-center bg-slate-900/80 backdrop-blur-sm px-4 py-3 rounded-xl border border-emerald-500/20 shadow-lg typing-effect">
                            <span className="mr-3 opacity-50 text-xs shrink-0">&gt;</span>
                            <span className="font-medium tracking-wide">{line}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* State 2: Loading Spinner */}
                    <div className={`absolute inset-0 flex flex-col items-center justify-center transition-opacity duration-500 ${simulationStage === 'loading' ? 'opacity-100 z-20' : 'opacity-0 z-0'}`}>
                      <div className="relative">
                        <div className="w-16 h-16 rounded-full border-4 border-emerald-500/30 border-t-emerald-500 animate-spin" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Sparkles className="w-6 h-6 text-emerald-400 animate-pulse" />
                        </div>
                      </div>
                      <p className="mt-4 text-emerald-400 font-mono text-sm tracking-widest uppercase animate-pulse">Finalizing...</p>
                    </div>

                    {/* State 3: Video Reveal */}
                    <div className={`absolute inset-0 transition-opacity duration-1000 ${simulationStage === 'video' ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}>
                      {/* GIF Placeholder - Visible while video loads */}
                      <img
                        src="/assets/serum-ad.gif"
                        alt="AI Video Generation Simulation"
                        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ${videoLoaded ? 'opacity-0' : 'opacity-90'}`}
                      />

                      {/* High Quality Video - Fades in when loaded */}
                      <video
                        src="/assets/serum-ad.mp4"
                        autoPlay
                        loop
                        muted={isMuted || simulationStage !== 'video'}
                        playsInline
                        onCanPlayThrough={() => setVideoLoaded(true)}
                        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ${videoLoaded ? 'opacity-90' : 'opacity-0'}`}
                      />

                      {/* Gradient overlays for depth */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent z-10" />
                      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 mix-blend-overlay z-10" />

                      {/* Volume Toggle */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsMuted(!isMuted);
                        }}
                        className={`absolute top-4 right-4 z-30 p-2.5 rounded-full bg-black/40 backdrop-blur-md border border-white/10 text-white/80 hover:text-white hover:bg-black/60 transition-all duration-300 ${videoLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}
                        aria-label={isMuted ? "Unmute video" : "Mute video"}
                      >
                        {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                      </button>
                    </div>

                  </div>

                  {/* Status indicators - ENHANCED */}
                  <div className="space-y-3.5">
                    {[
                      { label: 'Script Writing', status: 'complete', color: 'emerald' },
                      { label: 'Voice Synthesis', status: 'complete', color: 'emerald' },
                      { label: 'Rendering with Veo 3', status: 'processing', color: 'amber' }
                    ].map((item, idx) => (
                      <div key={idx} className={`flex items-center gap-3.5 text-${item.color}-400`}>
                        <div className={`w-6 h-6 rounded-full bg-${item.color}-500/20 flex items-center justify-center flex-shrink-0`}>
                          {item.status === 'complete' ? (
                            <Check className="w-3.5 h-3.5" strokeWidth={3} />
                          ) : (
                            <div className={`w-3.5 h-3.5 border-2 border-${item.color}-400 border-t-transparent rounded-full animate-spin`} />
                          )}
                        </div>
                        <span className="font-semibold text-sm">{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Features Section - REFINED */}
      <section id="features" className="relative py-32 px-6 bg-gradient-to-b from-transparent to-slate-950/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl lg:text-6xl font-extrabold mb-6">
              <span className="bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                Why Top Brands Switch to AI
              </span>
            </h2>
            <p className="text-slate-400 text-xl leading-relaxed mx-auto" style={{ maxWidth: '48rem' }}>
              Transform your creative workflow with AI-powered efficiency
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="glass-panel p-10 rounded-3xl group cursor-pointer hover:scale-[1.02] transition-all duration-500"
                >
                  <div className="icon-container w-20 h-20 rounded-2xl mb-8">
                    <Icon className="w-10 h-10 text-purple-400" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-white text-2xl font-extrabold mb-5 group-hover:text-purple-300 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-slate-400 leading-relaxed text-lg">
                    {feature.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pricing Section - ENHANCED */}
      <section id="pricing" className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-white text-5xl lg:text-6xl font-extrabold mb-6">
              Simple, Transparent Pricing
            </h2>
            <p className="text-slate-400 text-xl">
              Scale your ads, not your overhead.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, idx) => (
              <div
                key={idx}
                className={`glass-panel p-10 rounded-3xl relative transition-all duration-300 hover:scale-[1.02] ${plan.highlight
                  ? 'ring-2 ring-purple-500/50 shadow-[0_0_60px_rgba(139,92,246,0.4)]'
                  : ''
                  }`}
              >
                {plan.highlight && (
                  <div className="absolute -top-5 left-1/2 -translate-x-1/2 px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full text-sm font-bold shadow-xl text-white">
                    Most Popular
                  </div>
                )}
                {plan.badge && !plan.highlight && (
                  <div className="inline-flex items-center px-4 py-2 rounded-full text-xs font-bold bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-500/30 text-purple-200 mb-6 uppercase tracking-wider">
                    {plan.badge}
                  </div>
                )}

                <h3 className="text-white text-3xl font-black mb-3">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-6xl font-black bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    {plan.price}
                  </span>
                  <span className="text-slate-500 ml-3 text-lg">{plan.period}</span>
                </div>
                <p className="text-slate-400 mb-10 text-lg leading-relaxed min-h-[3.5rem]">{plan.description}</p>

                <a
                  href={`https://app.igniteai.in/pricing?plan=${plan.tier}`}
                  className={`block w-full text-center px-8 py-4 rounded-2xl font-bold transition-all duration-300 mb-10 text-lg ${plan.highlight
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:shadow-[0_0_40px_rgba(139,92,246,0.6)] hover:-translate-y-1 shadow-xl'
                    : 'bg-slate-800 text-white hover:bg-slate-700 hover:shadow-xl'
                    }`}
                >
                  {plan.cta}
                </a>

                <ul className="space-y-4">
                  {plan.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-3.5 text-slate-300 text-base">
                      <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="w-3.5 h-3.5 text-purple-400" strokeWidth={3} />
                      </div>
                      <span className="font-medium">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <p className="text-center text-slate-400 mt-16 text-lg">
            Estimate: <strong className="text-white font-bold">10-25</strong> credits per video (varies by duration & features)
          </p>
        </div>
      </section>

      <Footer />
    </div>
  );
}
