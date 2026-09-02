import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import api from '../services/api';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart as PieIcon, 
  ShieldCheck, 
  Sparkles,
  Calendar,
  Filter
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

import CashflowPredictor from '../components/Analytics/CashflowPredictor';
import { useAuth } from '../context/AuthContext';

const AnalyticsPage = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  // Date Range Controls
  const [selectedMonth, setSelectedMonth] = useState(() => new Date().toISOString().slice(0, 7));
  const [trendHorizon, setTrendHorizon] = useState(6);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [sumRes, catRes, trendRes] = await Promise.all([
        api.get(`/analytics/summary?month=${selectedMonth}`),
        api.get(`/analytics/categories?month=${selectedMonth}`),
        api.get(`/analytics/trends?month=${selectedMonth}&months_count=${trendHorizon}`)
      ]);

      setSummary(sumRes.data);
      setCategories(catRes.data);
      setTrends(trendRes.data);
    } catch (err) {
      console.error('Failed to load analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [selectedMonth, trendHorizon]);

  return (
    <Layout onRefreshData={fetchAnalytics}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-slate-800">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 mb-1">
              <BarChart3 className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Financial Insights</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">Analytics & Visualizations</h2>
            <p className="text-xs text-slate-400 mt-1">Deep dive into category spending, monthly trends, and saving habits.</p>
          </div>

          {/* Interactive Date Range & Horizon Selector */}
          <div className="flex flex-wrap items-center gap-3 bg-[#070D1F] p-2.5 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold text-slate-300">Month:</span>
              <input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-100 font-semibold focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
              <Filter className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold text-slate-300">Trend Horizon:</span>
              <select
                value={user?.role === 'student' && trendHorizon > 6 ? 6 : trendHorizon}
                onChange={(e) => setTrendHorizon(Number(e.target.value))}
                className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-100 font-semibold focus:outline-none focus:border-indigo-500"
              >
                <option value={3}>3 Months</option>
                <option value={6}>6 Months</option>
                {(user?.role === 'admin' || user?.role === 'premium') && (
                  <option value={12}>12 Months (Premium ⭐)</option>
                )}
              </select>
            </div>
          </div>
        </div>

        {/* Predictive Cashflow Velocity Predictor */}
        <CashflowPredictor month={selectedMonth} />

        {/* Top Summaries */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="glass-panel p-5 rounded-3xl border border-slate-800">
            <p className="text-xs text-slate-400 font-semibold uppercase">Financial Health Score</p>
            <h3 className="text-3xl font-extrabold text-emerald-400 mt-1">
              {summary ? (summary.savings_rate >= 20 ? '92 / 100' : '78 / 100') : '--'}
            </h3>
            <p className="text-[11px] text-slate-400 mt-1">
              {summary?.savings_rate >= 20 ? 'Optimal savings rate achieved!' : 'Try reducing non-essential expenses.'}
            </p>
          </div>

          <div className="glass-panel p-5 rounded-3xl border border-slate-800">
            <p className="text-xs text-slate-400 font-semibold uppercase">Current Savings Rate</p>
            <h3 className="text-3xl font-extrabold text-indigo-400 mt-1">{summary?.savings_rate || 0}%</h3>
            <p className="text-[11px] text-slate-400 mt-1">Percentage of income retained as savings</p>
          </div>

          <div className="glass-panel p-5 rounded-3xl border border-slate-800">
            <p className="text-xs text-slate-400 font-semibold uppercase">Monthly Net Surplus</p>
            <h3 className="text-3xl font-extrabold text-purple-400 mt-1">
              ${summary?.net_savings?.toLocaleString() || '0.00'}
            </h3>
            <p className="text-[11px] text-slate-400 mt-1">Income minus total expenses</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Comparison Bar Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="font-bold text-lg text-slate-100 mb-1">Monthly Income vs. Expense Comparison</h3>
            <p className="text-xs text-slate-400 mb-4">Historical comparison over recent months</p>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends}>
                  <XAxis dataKey="month" stroke="#64748B" fontSize={11} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                  <Legend />
                  <Bar dataKey="income" fill="#10B981" name="Income ($)" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="expense" fill="#EF4444" name="Expense ($)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Category Spending Donut Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="font-bold text-lg text-slate-100 mb-1">Category Spending Distribution</h3>
            <p className="text-xs text-slate-400 mb-4">Percentage breakdown by expense category</p>
            <div className="h-72 w-full flex items-center justify-center">
              {categories.length === 0 ? (
                <p className="text-xs text-slate-500">No data available for charts.</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories}
                      dataKey="amount"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      innerRadius={50}
                      paddingAngle={4}
                      label={({ category, percentage }) => `${category} (${percentage}%)`}
                    >
                      {categories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AnalyticsPage;
