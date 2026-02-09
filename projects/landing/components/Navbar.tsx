'use client';

import Link from 'next/link';

export default function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 px-6 sm:px-8 lg:px-12 py-6">
            <div className="max-w-7xl mx-auto flex justify-between items-center glass-card rounded-2xl px-6 py-4">
                <Link href="/" className="flex items-center gap-1 font-extrabold text-2xl -tracking-tight group">
                    <span className="bg-gradient-to-br from-white to-slate-300 bg-clip-text text-transparent group-hover:from-purple-200 group-hover:to-white transition-all duration-300">
                        IGNITE
                    </span>
                    <span className="font-light bg-gradient-to-br from-purple-400 to-indigo-400 bg-clip-text text-transparent group-hover:from-purple-300 group-hover:to-indigo-300 transition-all duration-300">
                        AI
                    </span>
                </Link>

                <div className="flex gap-8 items-center">
                    <a
                        href="#features"
                        className="text-slate-400 hover:text-white transition-colors font-medium hidden sm:block"
                    >
                        Features
                    </a>
                    <a
                        href="#pricing"
                        className="text-slate-400 hover:text-white transition-colors font-medium hidden sm:block"
                    >
                        Pricing
                    </a>
                    <Link
                        href="https://app.igniteai.in/sign-in"
                        className="px-6 py-2.5 rounded-lg font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:-translate-y-0.5 transition-all duration-300"
                    >
                        Sign In
                    </Link>
                </div>
            </div>
        </nav>
    );
}
