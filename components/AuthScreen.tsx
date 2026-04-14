
import React, { useState } from 'react';
import { mockApi } from '../services/api';

interface AuthScreenProps {
  onAuthSuccess: () => void;
}

const AuthScreen: React.FC<AuthScreenProps> = ({ onAuthSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await mockApi.login(email, password);
      onAuthSuccess();
    } catch (err: any) {
      setError(err.message || 'Ошибка авторизации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 p-6 relative overflow-hidden">
      {/* Декоративные элементы фона */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-600/10 blur-[120px] rounded-full"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-indigo-600 rounded-[24px] flex items-center justify-center text-white shadow-2xl shadow-indigo-600/40 mx-auto mb-6 rotate-3 transition-transform hover:rotate-0 duration-500">
            <i className="fas fa-radar fa-3x"></i>
          </div>
          <h1 className="text-4xl font-black text-white tracking-tighter mb-2">TenderPulse AI</h1>
          <p className="text-slate-400 font-medium">Вход в систему мониторинга</p>
        </div>

        <div className="bg-white/10 backdrop-blur-xl border border-white/10 p-10 rounded-[40px] shadow-2xl">
          <h2 className="text-white text-xl font-bold mb-8 text-center uppercase tracking-widest text-[14px]">Авторизация</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Логин / Email</label>
              <div className="relative">
                <i className="fas fa-envelope absolute left-5 top-1/2 -translate-y-1/2 text-slate-500"></i>
                <input 
                  type="text" required value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="admin_pavel"
                  className="w-full bg-slate-800/50 border border-white/5 px-12 py-4 rounded-2xl text-white placeholder:text-slate-600 focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Пароль</label>
              <div className="relative">
                <i className="fas fa-lock absolute left-5 top-1/2 -translate-y-1/2 text-slate-500"></i>
                <input 
                  type="password" required value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-800/50 border border-white/5 px-12 py-4 rounded-2xl text-white placeholder:text-slate-600 focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
            </div>

            {error && (
              <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-2xl text-sm font-bold flex items-center gap-3 animate-shake">
                <i className="fas fa-exclamation-circle"></i>
                {error}
              </div>
            )}

            <button 
              type="submit" disabled={loading}
              className="w-full bg-indigo-600 text-white py-5 rounded-2xl font-black uppercase tracking-widest shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-3 mt-4"
            >
              {loading ? (
                <i className="fas fa-spinner fa-spin"></i>
              ) : (
                <>
                  Войти в систему
                  <i className="fas fa-arrow-right text-xs"></i>
                </>
              )}
            </button>

            <div className="relative flex items-center justify-center py-2">
              <div className="flex-grow border-t border-white/5"></div>
              <span className="flex-shrink mx-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Или</span>
              <div className="flex-grow border-t border-white/5"></div>
            </div>

            <button 
              type="button"
              onClick={() => { setEmail('demo'); setPassword('demo'); handleSubmit({ preventDefault: () => {} } as any); }}
              className="w-full bg-slate-800 text-slate-300 py-4 rounded-2xl font-bold uppercase tracking-widest hover:bg-slate-700 transition-all flex items-center justify-center gap-3"
            >
              Демо-вход
              <i className="fas fa-flask text-xs"></i>
            </button>
          </form>
        </div>

        <p className="text-center mt-8 text-slate-500 text-sm">
          Доступ разрешен только зарегистрированным сотрудникам.
        </p>
      </div>
    </div>
  );
};

export default AuthScreen;
