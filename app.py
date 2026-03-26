import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { 
  calculateMonthTotal, 
  calculateAnnualRecovery, 
  calculateQuarterlyRecovery, 
  QUARTERS, 
  formatCurrency, 
  MONTHS 
} from "@/lib/compensation";
import { motion } from "framer-motion";
import { 
  ComposedChart, 
  Bar, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  Legend 
} from 'recharts';
import SummaryCard from "@/components/dashboard/SummaryCard";
import { Award, TrendingUp, DollarSign, Target, CheckCircle2 } from "lucide-react";

export default function AnnualView() {
  const [profile, setProfile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const currentUser = await base44.auth.me();
      const profiles = await base44.entities.UserProfile.filter({ created_by: currentUser.email });
      const monthlyResults = await base44.entities.MonthlyResult.filter(
        { created_by: currentUser.email }, 'month_number'
      );
      if (profiles.length > 0) setProfile(profiles[0]);
      setResults(monthlyResults);
      setLoading(false);
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const salary = profile?.salary || 0;
  const targetSal = profile?.target_salaries || 0.43;
  const annualResult = calculateAnnualRecovery(results, salary, targetSal);

  // Quarterly summaries com Meta vs Real
  const quarterData = Object.entries(QUARTERS).map(([qKey, months]) => {
    const qMonths = months.map(m => results.find(r => r.month_number === m)).filter(Boolean);
    const qResult = calculateQuarterlyRecovery(qMonths, salary, targetSal);
    
    // Cálculo de meta trimestral (supondo que o target_value venha do banco)
    const qTarget = qMonths.reduce((sum, m) => sum + (m.target_value || 0), 0);
    const performance = qTarget > 0 ? (qResult.rvMonthly / (qTarget * targetSal * salary)) * 100 : 0;

    return { 
      name: qKey, 
      target: qTarget * targetSal * salary,
      performance,
      ...qResult 
    };
  });

  // Monthly breakdown para o gráfico (Meta vs Real)
  const monthlyChartData = MONTHS.map((month, idx) => {
    const monthData = results.find(m => m.month_number === idx + 1);
    const ponderado = monthData ? calculateMonthTotal(monthData) : 0;
    const realRV = ponderado * targetSal * salary;
    const metaRV = (monthData?.target_value || 0) * targetSal * salary;

    return { 
      name: month.substring(0, 3), 
      rv: realRV, 
      meta: metaRV 
    };
  });

  const totalQuarterlyRecovery = quarterData.reduce((sum, q) => sum + (q.rvRecovery || 0), 0);
  const avgPerformance = quarterData.reduce((sum, q) => sum + q.performance, 0) / 4;

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Resumo Anual de Performance</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Consolidado de metas e recuperação — {profile?.year || "2026"}
          </p>
        </div>
        <div className="hidden sm:block text-right">
          <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
            Status: {avgPerformance >= 100 ? "Meta Batida" : "Em Evolução"}
          </span>
        </div>
      </div>

      {/* Grid de Sumários */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="RV Anual (Real)"
          value={formatCurrency(annualResult.rvTotal)}
          icon={DollarSign}
          color="green"
        />
        <SummaryCard
          title="Atingimento Médio"
          value={`${avgPerformance.toFixed(1)}%`}
          icon={Target}
          color="primary"
          subtitle="Performance vs Meta"
        />
        <SummaryCard
          title="Recup. Trimestral"
          value={formatCurrency(totalQuarterlyRecovery)}
          icon={TrendingUp}
          color="accent"
          subtitle="Soma dos gatilhos Qs"
        />
        <SummaryCard
          title="Net Recovery"
          value={formatCurrency(annualResult.rvRecovery)}
          icon={CheckCircle2}
          color="amber"
          subtitle="75% de retenção anual"
        />
      </div>

      {/* Gráfico Meta vs Real */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card rounded-xl border border-border shadow-sm p-6"
      >
        <h3 className="font-semibold text-foreground mb-6">Realizado vs Meta (Mensal)</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={monthlyChartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }}
                formatter={(value) => [formatCurrency(value)]}
              />
              <Legend verticalAlign="top" height={36}/>
              <Bar dataKey="rv" name="RV Real" radius={[4, 4, 0, 0]}>
                {monthlyChartData.map((entry, index) => (
                  <Cell key={index} fill={entry.rv >= entry.meta ? 'hsl(var(--primary))' : '#94a3b8'} />
                ))}
              </Bar>
              <Line type="monotone" dataKey="meta" name="Meta Estipulada" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Tabela de Resultados por Q */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card rounded-xl border border-border shadow-sm overflow-hidden"
      >
        <div className="px-6 py-4 border-b border-border bg-muted/20">
          <h3 className="font-semibold text-foreground">Detalhamento por Trimestre (Qs)</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-border bg-muted/50 text-muted-foreground font-medium">
                <th className="px-6 py-4">Trimestre</th>
                <th className="px-4 py-4 text-right">Meta (RV)</th>
                <th className="px-4 py-4 text-right">Real (RV)</th>
                <th className="px-4 py-4 text-center">Atingimento (%)</th>
                <th className="px-6 py-4 text-right">Recuperação</th>
              </tr>
            </thead>
            <tbody>
              {quarterData.map((q) => (
                <tr key={q.name} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 font-bold text-foreground">{q.name}</td>
                  <td className="px-4 py-4 text-right text-muted-foreground">{formatCurrency(q.target)}</td>
                  <td className="px-4 py-4 text-right font-medium">{formatCurrency(q.rvMonthly)}</td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col items-center">
                      <span className={`text-xs font-bold ${q.performance >= 100 ? 'text-emerald-600' : 'text-amber-600'}`}>
                        {q.performance.toFixed(1)}%
                      </span>
                      <div className="w-20 h-1.5 bg-muted rounded-full mt-1 overflow-hidden">
                        <div 
                          className={`h-full ${q.performance >= 100 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                          style={{ width: `${Math.min(q.performance, 100)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right font-bold text-emerald-600">
                    {formatCurrency(q.rvRecovery)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-muted/50 font-bold">
              <tr>
                <td className="px-6 py-4">Consolidado Anual</td>
                <td colSpan={2} />
                <td className="px-4 py-4 text-center text-primary">{avgPerformance.toFixed(1)}%</td>
                <td className="px-6 py-4 text-right text-emerald-600">{formatCurrency(annualResult.rvRecovery)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
