import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, AlertTriangle, Info, X, Trash2, PlusCircle, Sparkles } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success', duration = 3500) => {
    const id = Date.now() + Math.random().toString();
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = {
    success: (msg, dur) => addToast(msg, 'success', dur),
    info: (msg, dur) => addToast(msg, 'info', dur),
    warning: (msg, dur) => addToast(msg, 'warning', dur),
    error: (msg, dur) => addToast(msg, 'error', dur),
    delete: (msg, dur) => addToast(msg, 'delete', dur),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast Notification Container */}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center justify-between p-4 rounded-2xl border shadow-2xl backdrop-blur-xl transition-all duration-300 transform translate-y-0 animate-slide-in ${
              t.type === 'success'
                ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-100 shadow-emerald-950/50'
                : t.type === 'delete' || t.type === 'info'
                ? 'bg-slate-900/95 border-cyan-500/40 text-slate-100 shadow-slate-950/50'
                : t.type === 'warning'
                ? 'bg-amber-950/90 border-amber-500/40 text-amber-100 shadow-amber-950/50'
                : 'bg-rose-950/90 border-rose-500/40 text-rose-100 shadow-rose-950/50'
            }`}
          >
            <div className="flex items-center gap-3 pr-2">
              <div className="shrink-0">
                {t.type === 'success' && (
                  <div className="p-1.5 rounded-xl bg-emerald-500/20 text-emerald-400">
                    <CheckCircle className="w-5 h-5" />
                  </div>
                )}
                {t.type === 'delete' && (
                  <div className="p-1.5 rounded-xl bg-rose-500/20 text-rose-400">
                    <Trash2 className="w-5 h-5" />
                  </div>
                )}
                {t.type === 'info' && (
                  <div className="p-1.5 rounded-xl bg-cyan-500/20 text-cyan-400">
                    <Info className="w-5 h-5" />
                  </div>
                )}
                {t.type === 'warning' && (
                  <div className="p-1.5 rounded-xl bg-amber-500/20 text-amber-400">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                )}
                {t.type === 'error' && (
                  <div className="p-1.5 rounded-xl bg-rose-500/20 text-rose-400">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                )}
              </div>

              <div>
                <h5 className="text-xs font-extrabold capitalize tracking-wide">
                  {t.type === 'delete' ? 'Item Deleted 🗑️' : t.type === 'success' ? 'Success ✓' : t.type === 'warning' ? 'Warning ⚠️' : 'Notification'}
                </h5>
                <p className="text-xs font-medium text-slate-200 mt-0.5 leading-snug">{t.message}</p>
              </div>
            </div>

            <button
              onClick={() => removeToast(t.id)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
