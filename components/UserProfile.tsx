
import React, { useState } from 'react';
import { mockApi } from '../services/api';

const UserProfile: React.FC = () => {
  const [formData, setFormData] = useState({
    current_password: '',
    new_email: '',
    new_password: '',
    confirm_password: '',
    kontur_login: '',
    kontur_password: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (formData.new_password && formData.new_password !== formData.confirm_password) {
      setMessage({ text: 'Новые пароли не совпадают', type: 'error' });
      return;
    }

    if (!formData.current_password) {
      setMessage({ text: 'Введите текущий пароль для подтверждения изменений', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const payload: any = { current_password: formData.current_password };
      if (formData.new_email) payload.new_email = formData.new_email;
      if (formData.new_password) payload.new_password = formData.new_password;
      if (formData.kontur_login) payload.kontur_login = formData.kontur_login;
      if (formData.kontur_password) payload.kontur_password = formData.kontur_password;

      const response = await mockApi.updateProfile(payload);
      setMessage({ text: response.message || 'Данные успешно обновлены', type: 'success' });
      
      // Сбрасываем поля подтверждения и паролей
      setFormData(prev => ({
        ...prev,
        current_password: '',
        new_password: '',
        confirm_password: ''
      }));
    } catch (err: any) {
      setMessage({ text: err.message || 'Ошибка при обновлении профиля', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 max-w-3xl mx-auto">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-black text-slate-800 tracking-tight">Личный кабинет</h2>
        <p className="text-slate-500 mt-1">Управление учетными данными и безопасностью аккаунта</p>
      </div>

      <div className="flex flex-col gap-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Section */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-200 shadow-sm space-y-6 transition-all hover:shadow-md">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[3px] mb-2 flex items-center gap-2">
              <i className="fas fa-envelope text-indigo-500"></i> Основные данные
            </h4>
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Новый Email (необязательно)</label>
              <input 
                type="email" 
                value={formData.new_email} 
                onChange={e => setFormData({...formData, new_email: e.target.value})}
                placeholder="Оставьте пустым, если не хотите менять"
                className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
              />
            </div>
          </div>

          {/* Kontur Section */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-200 shadow-sm space-y-6 transition-all hover:shadow-md">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[3px] flex items-center gap-2">
                <i className="fas fa-robot text-emerald-500"></i> Kontur.Zakupki Credentials
              </h4>
              <span className="text-[9px] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded font-black uppercase tracking-wider">Для скрапера</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Логин Контур</label>
                <input 
                  type="text" 
                  value={formData.kontur_login} 
                  onChange={e => setFormData({...formData, kontur_login: e.target.value})}
                  placeholder="Login / Phone"
                  className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Пароль Контур</label>
                <input 
                  type="password" 
                  value={formData.kontur_password} 
                  onChange={e => setFormData({...formData, kontur_password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
            </div>
          </div>

          {/* Password Section */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-200 shadow-sm space-y-6 transition-all hover:shadow-md">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[3px] mb-2 flex items-center gap-2">
              <i className="fas fa-key text-indigo-500"></i> Смена пароля платформы
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Новый пароль</label>
                <input 
                  type="password" 
                  value={formData.new_password} 
                  onChange={e => setFormData({...formData, new_password: e.target.value})}
                  placeholder="Минимум 6 символов"
                  className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Повторите пароль</label>
                <input 
                  type="password" 
                  value={formData.confirm_password} 
                  onChange={e => setFormData({...formData, confirm_password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                />
              </div>
            </div>
          </div>

          {/* Confirmation & Submit */}
          <div className="bg-indigo-600 p-8 rounded-[32px] shadow-xl shadow-indigo-600/20 space-y-6 border border-indigo-400/20">
            <h4 className="text-[10px] font-black text-indigo-200 uppercase tracking-[3px] mb-2">Подтверждение изменений</h4>
            <div className="space-y-2">
              <label className="text-[10px] font-black text-indigo-300 uppercase tracking-widest block ml-1">Текущий пароль</label>
              <input 
                type="password" 
                required 
                value={formData.current_password} 
                onChange={e => setFormData({...formData, current_password: e.target.value})}
                placeholder="Введите текущий пароль для сохранения всех полей"
                className="w-full bg-indigo-500/30 border border-indigo-400/30 px-6 py-4 rounded-2xl text-white placeholder:text-indigo-300/60 focus:ring-4 focus:ring-white/10 focus:border-white focus:outline-none transition-all font-medium"
              />
            </div>

            {message && (
              <div className={`p-4 rounded-2xl text-sm font-bold flex items-center gap-3 animate-in fade-in slide-in-from-top-2 ${
                message.type === 'success' ? 'bg-emerald-400/20 text-emerald-100 border border-emerald-400/20' : 'bg-rose-400/20 text-rose-100 border border-rose-400/20'
              }`}>
                <i className={`fas ${message.type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}`}></i>
                {message.text}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-white text-indigo-600 py-5 rounded-2xl font-black uppercase tracking-widest shadow-xl hover:bg-indigo-50 active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-3"
            >
              {loading ? <i className="fas fa-spinner fa-spin"></i> : 'Сохранить данные'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserProfile;
