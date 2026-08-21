import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import StatCard from '../components/Common/StatCard';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import CashflowPredictor from '../components/Analytics/CashflowPredictor';
import { 
  Wallet, 
  Receipt, 
  PiggyBank, 
  Target, 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight,
  Sparkles,
  Plus
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [trends, setTrends] = useState([]);
  const [recentExpenses, setRecentExpenses] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [sumRes, catRes, trendRes, expRes, budRes, goalRes] = await Promise.all([
        api.get('/analytics/summary'),
        api.get('/analytics/categories'),
        api.get('/analytics/trends'),
        api.get('/expenses/?limit=5'),
        api.get('/budgets/'),
        api.get('/savings/')
      ]);

      setSummary(sumRes.data);
      setCategories(catRes.data);
      setTrends(trendRes.data);
      setRecentExpenses(expRes.data.slice(0, 5));
      setBudgets(budRes.data);
      setGoals(goalRes.data.slice(0, 3));
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <Layout onRefreshData={fetchDashboardData}>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-slate-800">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 mb-1">
              <Sparkles className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Overview Dashboard</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white">
              Welcome back, {user?.full_name?.split(' ')[0]}! 👋
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Here is your financial summary and monthly budget utilization performance.
            </p>
          </div>
        </div>

        {/* Top Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Monthly Income"
            amount={`$${summary?.total_income?.toLocaleString() || '0.00'}`}
            subtitle="Current month incoming"
            icon={Wallet}
            color="emerald"
            onClick={() => navigate('/income')}
          />
          <StatCard
            title="Total Monthly Expense"
            amount={`$${summary?.total_expense?.toLocaleString() || '0.00'}`}
            subtitle="Current month total spent"
            icon={Receipt}
            color="rose"
            onClick={() => navigate('/expenses')}
          />
          <StatCard
            title="Net Savings Balance"
            amount={`$${summary?.net_savings?.toLocaleString() || '0.00'}`}
            subtitle={`Savings Rate: ${summary?.savings_rate || 0}%`}
            icon={PiggyBank}
            color="indigo"
            onClick={() => navigate('/budgets')}
          />
          <StatCard
            title="Active Savings Goals"
            amount={summary?.active_goals_count || 0}
            subtitle="In-progress targets"
            icon={Target}
            color="purple"
            onClick={() => navigate('/savings')}
          />
        </div>

        {/* Month-End Cashflow Predictor & Velocity Forecast */}
        <CashflowPredictor />

        {/* Charts & Graphs Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Monthly Trend Chart */}
          <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-lg text-slate-100">Income vs. Expense Trend</h3>
                <p className="text-xs text-slate-400">Monthly financial comparison over time</p>
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="incomeColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="expenseColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="income" stroke="#10B981" fillOpacity={1} fill="url(#incomeColor)" name="Income ($)" />
                  <Area type="monotone" dataKey="expense" stroke="#EF4444" fillOpacity={1} fill="url(#expenseColor)" name="Expense ($)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Category Spending Breakdown */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-lg text-slate-100 mb-1">Category Breakdown</h3>
              <p className="text-xs text-slate-400 mb-4">Expense distribution this month</p>
              <div className="h-48 w-full relative flex items-center justify-center">
                {categories.length === 0 ? (
                  <p className="text-xs text-slate-500">No expenses recorded yet.</p>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={categories}
                        dataKey="amount"
                        nameKey="category"
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={70}
                        paddingAngle={4}
                      >
                        {categories.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Category Badges */}
            <div className="grid grid-cols-2 gap-2 mt-2">
              {categories.slice(0, 4).map((c, i) => (
                <div key={c.category} className="flex items-center gap-2 text-xs">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="text-slate-300 truncate">{c.category} ({c.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lower Grid: Recent Transactions & Active Savings */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Expenses List */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-lg text-slate-100">Recent Transactions</h3>
              <span className="text-xs text-indigo-400 font-semibold">Latest Expenses</span>
            </div>
            <div className="space-y-3">
              {recentExpenses.length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">No transaction records found.</p>
              ) : (
                recentExpenses.map((exp) => (
                  <div key={exp.id} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <ArrowDownRight className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-slate-200">{exp.title}</h4>
                        <span className="text-[11px] text-slate-400">{exp.category} • {exp.payment_method}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-rose-400">-${exp.amount.toFixed(2)}</p>
                      <p className="text-[10px] text-slate-500">{new Date(exp.date).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Active Savings Progress */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-lg text-slate-100">Savings Goals Milestone</h3>
              <span className="text-xs text-purple-400 font-semibold">Target Tracker</span>
            </div>
            <div className="space-y-4">
              {goals.length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">No active savings goals.</p>
              ) : (
                goals.map((g) => (
                  <div key={g.id} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200">{g.title}</span>
                      <span className="text-indigo-400 font-bold">${g.current_amount} / ${g.target_amount}</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                        style={{ width: `${g.progress_percentage}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>{g.category}</span>
                      <span className="font-semibold text-purple-300">{g.progress_percentage}% achieved</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
