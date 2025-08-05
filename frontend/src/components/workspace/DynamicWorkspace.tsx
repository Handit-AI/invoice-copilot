import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer 
} from 'recharts';

// REAL DATA extracted from provided invoice files
const invoiceData = [
  { invoice: 'Invoice 1', amount: 634.73, date: '2024-08-01', company: 'Smith Enterprises' },
  { invoice: 'Invoice 2', amount: 440.00, date: '2030-11-02', company: 'Thynk Unlimited' },
  { invoice: 'Invoice 3', amount: 685.35, date: '2018-04-11', company: 'ACME' },
  { invoice: 'Invoice 4', amount: 248.98, date: '2025-01-02', company: 'Your Company Name' }
];

export function DynamicWorkspace() {
  const { state } = useApp();
  const { workspaceContent } = state;

  // Calculate REAL metrics from invoice data
  const totalExpenses = invoiceData.reduce((acc, curr) => acc + curr.amount, 0);
  const totalInvoices = invoiceData.length;
  const averageAmount = totalInvoices ? (totalExpenses / totalInvoices).toFixed(2) : 0;

  // Prepare data for LineChart (monthly trend)
  const monthlyData = invoiceData.map(item => ({
    month: item.date,
    amount: item.amount
  }));

  // Prepare data for PieChart (company distribution)
  const companyData = invoiceData.reduce((acc, curr) => {
    const existing = acc.find(item => item.name === curr.company);
    if (existing) {
      existing.value += curr.amount;
    } else {
      acc.push({ name: curr.company, value: curr.amount });
    }
    return acc;
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Invoice Analysis Report</h1>
        <p className="text-gray-600 mt-2">Real data insights from processed invoices</p>
      </div>
      
      {/* Key Metrics Cards with REAL values */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Total Expenses</h3>
          <p className="text-3xl font-bold text-blue-600">${totalExpenses.toFixed(2)}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Total Invoices</h3>
          <p className="text-3xl font-bold text-green-600">{totalInvoices}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Average Amount</h3>
          <p className="text-3xl font-bold text-purple-600">${averageAmount}</p>
        </div>
      </div>
      
      {/* Charts using Recharts with REAL data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Invoice Amounts</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={invoiceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="invoice" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="amount" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Company Distribution</h3>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={companyData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {companyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`#${(index * 123456).toString(16).slice(0, 6)}`} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Monthly Amount Trend */}
      <div className="bg-white p-6 rounded-lg shadow mt-6">
        <h3 className="text-lg font-semibold mb-4">Monthly Amount Trend</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="amount" stroke="#82ca9d" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}