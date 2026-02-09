import Link from 'next/link';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="relative border-t border-white/5 px-6 sm:px-8 lg:px-12 py-16 bg-gradient-to-t from-slate-950 to-transparent">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12">
                    {/* Company Info */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-1 font-extrabold text-xl -tracking-tight mb-4">
                            <span className="bg-gradient-to-br from-white to-slate-300 bg-clip-text text-transparent">
                                IGNITE
                            </span>
                            <span className="font-light bg-gradient-to-br from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                                AI
                            </span>
                        </div>
                        <p className="text-slate-400">
                            by <strong className="text-white">The Jaggery Point</strong>
                        </p>
                        <p className="text-sm text-slate-500 leading-relaxed">
                            Built on Google Cloud AI and scalable cloud infrastructure.
                        </p>
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-slate-400 text-sm">
                            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                            Currently in private beta
                        </div>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">Legal</h4>
                        <div className="space-y-3">
                            {['Terms and Conditions', 'Privacy Policy', 'Shipping Policy', 'Cancellation & Refunds'].map((item, idx) => {
                                const href = '/' + item.toLowerCase().replace(/ & /g, '-').replace(/ /g, '-');
                                return (
                                    <Link
                                        key={idx}
                                        href={href}
                                        className="block text-slate-400 hover:text-purple-400 transition-colors"
                                    >
                                        {item}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>

                    {/* Support */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">Support</h4>
                        <Link
                            href="/contact"
                            className="block text-slate-400 hover:text-purple-400 transition-colors"
                        >
                            Contact Us
                        </Link>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-slate-500">
                    <p>© {currentYear} The Jaggery Point. All rights reserved.</p>
                    <p className="font-mono text-xs">Built with Next.js & Tailwind CSS</p>
                </div>
            </div>
        </footer>
    );
}
