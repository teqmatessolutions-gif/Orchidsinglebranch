import React, { useState, useEffect } from "react";
import DashboardLayout from "../layout/DashboardLayout";
import api from "../services/api";
import { 
  BookOpen, 
  FileText, 
  Calculator, 
  Plus, 
  Edit, 
  Trash2, 
  Search,
  DollarSign,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle
} from "lucide-react";

export default function Accounting() {
  const [activeTab, setActiveTab] = useState("chart-of-accounts");
  const [loading, setLoading] = useState(false);
  
  // Chart of Accounts State
  const [accountGroups, setAccountGroups] = useState([]);
  const [accountLedgers, setAccountLedgers] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [showLedgerModal, setShowLedgerModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [editingLedger, setEditingLedger] = useState(null);
  
  // Journal Entries State
  const [journalEntries, setJournalEntries] = useState([]);
  const [showJournalModal, setShowJournalModal] = useState(false);
  
  // Trial Balance State
  const [trialBalance, setTrialBalance] = useState(null);
  
  // Form States
  const [groupForm, setGroupForm] = useState({
    name: "",
    account_type: "Revenue",
    description: ""
  });
  
  const [ledgerForm, setLedgerForm] = useState({
    name: "",
    code: "",
    group_id: "",
    module: "",
    description: "",
    opening_balance: 0,
    balance_type: "debit",
    tax_type: "",
    tax_rate: "",
    bank_name: "",
    account_number: "",
    ifsc_code: "",
    branch_name: ""
  });
  
  const [journalForm, setJournalForm] = useState({
    entry_date: new Date().toISOString().split('T')[0],
    description: "",
    notes: "",
    lines: [{ debit_ledger_id: "", credit_ledger_id: "", amount: 0, description: "" }]
  });

  // Fetch Data
  useEffect(() => {
    if (activeTab === "chart-of-accounts") {
      fetchAccountGroups();
      fetchAccountLedgers();
    } else if (activeTab === "journal-entries") {
      fetchJournalEntries();
    } else if (activeTab === "trial-balance") {
      fetchTrialBalance();
    }
  }, [activeTab]);

  const fetchAccountGroups = async () => {
    try {
      const res = await api.get("/accounts/groups?limit=1000");
      setAccountGroups(res.data || []);
    } catch (error) {
      console.error("Failed to fetch account groups:", error);
      alert("Failed to load account groups");
    }
  };

  const fetchAccountLedgers = async () => {
    try {
      const res = await api.get("/accounts/ledgers?limit=1000");
      setAccountLedgers(res.data || []);
    } catch (error) {
      console.error("Failed to fetch account ledgers:", error);
      alert("Failed to load account ledgers");
    }
  };

  const fetchJournalEntries = async () => {
    try {
      setLoading(true);
      const res = await api.get("/accounts/journal-entries?limit=100");
      setJournalEntries(res.data || []);
    } catch (error) {
      console.error("Failed to fetch journal entries:", error);
      alert("Failed to load journal entries");
    } finally {
      setLoading(false);
    }
  };

  const fetchTrialBalance = async () => {
    try {
      setLoading(true);
      const res = await api.get("/accounts/trial-balance");
      setTrialBalance(res.data);
    } catch (error) {
      console.error("Failed to fetch trial balance:", error);
      alert("Failed to load trial balance");
    } finally {
      setLoading(false);
    }
  };

  // Account Group Handlers
  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      if (editingGroup) {
        await api.put(`/accounts/groups/${editingGroup.id}`, groupForm);
      } else {
        await api.post("/accounts/groups", groupForm);
      }
      setShowGroupModal(false);
      setEditingGroup(null);
      setGroupForm({ name: "", account_type: "Revenue", description: "" });
      fetchAccountGroups();
    } catch (error) {
      alert(error.response?.data?.detail || "Failed to save account group");
    }
  };

  const handleDeleteGroup = async (id) => {
    if (!confirm("Are you sure you want to delete this account group?")) return;
    try {
      await api.delete(`/accounts/groups/${id}`);
      fetchAccountGroups();
    } catch (error) {
      alert("Failed to delete account group");
    }
  };

  // Account Ledger Handlers
  const handleCreateLedger = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...ledgerForm,
        group_id: parseInt(ledgerForm.group_id),
        opening_balance: parseFloat(ledgerForm.opening_balance) || 0,
        tax_rate: ledgerForm.tax_rate ? parseFloat(ledgerForm.tax_rate) : null
      };
      
      if (editingLedger) {
        await api.put(`/accounts/ledgers/${editingLedger.id}`, payload);
      } else {
        await api.post("/accounts/ledgers", payload);
      }
      setShowLedgerModal(false);
      setEditingLedger(null);
      setLedgerForm({
        name: "", code: "", group_id: "", module: "", description: "",
        opening_balance: 0, balance_type: "debit", tax_type: "", tax_rate: "",
        bank_name: "", account_number: "", ifsc_code: "", branch_name: ""
      });
      fetchAccountLedgers();
    } catch (error) {
      alert(error.response?.data?.detail || "Failed to save account ledger");
    }
  };

  const handleDeleteLedger = async (id) => {
    if (!confirm("Are you sure you want to delete this account ledger?")) return;
    try {
      await api.delete(`/accounts/ledgers/${id}`);
      fetchAccountLedgers();
    } catch (error) {
      alert("Failed to delete account ledger");
    }
  };

  // Journal Entry Handlers
  const handleAddJournalLine = () => {
    setJournalForm({
      ...journalForm,
      lines: [...journalForm.lines, { debit_ledger_id: "", credit_ledger_id: "", amount: 0, description: "" }]
    });
  };

  const handleRemoveJournalLine = (index) => {
    setJournalForm({
      ...journalForm,
      lines: journalForm.lines.filter((_, i) => i !== index)
    });
  };

  const handleCreateJournalEntry = async (e) => {
    e.preventDefault();
    try {
      // Validate debits equal credits
      const totalDebits = journalForm.lines
        .filter(line => line.debit_ledger_id)
        .reduce((sum, line) => sum + (parseFloat(line.amount) || 0), 0);
      const totalCredits = journalForm.lines
        .filter(line => line.credit_ledger_id)
        .reduce((sum, line) => sum + (parseFloat(line.amount) || 0), 0);
      
      if (Math.abs(totalDebits - totalCredits) > 0.01) {
        alert(`Journal entry must balance. Debits: ₹${totalDebits.toFixed(2)}, Credits: ₹${totalCredits.toFixed(2)}`);
        return;
      }
      
      const payload = {
        ...journalForm,
        entry_date: new Date(journalForm.entry_date).toISOString(),
        lines: journalForm.lines.map(line => ({
          ...line,
          debit_ledger_id: line.debit_ledger_id ? parseInt(line.debit_ledger_id) : null,
          credit_ledger_id: line.credit_ledger_id ? parseInt(line.credit_ledger_id) : null,
          amount: parseFloat(line.amount) || 0
        }))
      };
      
      await api.post("/accounts/journal-entries", payload);
      setShowJournalModal(false);
      setJournalForm({
        entry_date: new Date().toISOString().split('T')[0],
        description: "",
        notes: "",
        lines: [{ debit_ledger_id: "", credit_ledger_id: "", amount: 0, description: "" }]
      });
      fetchJournalEntries();
    } catch (error) {
      alert(error.response?.data?.detail || "Failed to create journal entry");
    }
  };

  const getLedgerName = (ledgerId) => {
    const ledger = accountLedgers.find(l => l.id === ledgerId);
    return ledger ? ledger.name : `Ledger #${ledgerId}`;
  };

  const filteredLedgers = selectedGroup
    ? accountLedgers.filter(l => l.group_id === selectedGroup.id)
    : accountLedgers;

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-800">Accounting Module</h1>
        </div>

        {/* Tabs */}
        <div className="flex space-x-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab("chart-of-accounts")}
            className={`px-4 py-2 font-medium ${
              activeTab === "chart-of-accounts"
                ? "border-b-2 border-indigo-600 text-indigo-600"
                : "text-gray-600 hover:text-gray-800"
            }`}
          >
            <BookOpen className="inline mr-2" size={18} />
            Chart of Accounts
          </button>
          <button
            onClick={() => setActiveTab("journal-entries")}
            className={`px-4 py-2 font-medium ${
              activeTab === "journal-entries"
                ? "border-b-2 border-indigo-600 text-indigo-600"
                : "text-gray-600 hover:text-gray-800"
            }`}
          >
            <FileText className="inline mr-2" size={18} />
            Journal Entries
          </button>
          <button
            onClick={() => setActiveTab("trial-balance")}
            className={`px-4 py-2 font-medium ${
              activeTab === "trial-balance"
                ? "border-b-2 border-indigo-600 text-indigo-600"
                : "text-gray-600 hover:text-gray-800"
            }`}
          >
            <Calculator className="inline mr-2" size={18} />
            Trial Balance
          </button>
        </div>

        {/* Chart of Accounts Tab */}
        {activeTab === "chart-of-accounts" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Account Groups */}
            <div className="lg:col-span-1 bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Account Groups</h2>
                <button
                  onClick={() => {
                    setEditingGroup(null);
                    setGroupForm({ name: "", account_type: "Revenue", description: "" });
                    setShowGroupModal(true);
                  }}
                  className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                  <Plus size={16} className="inline mr-1" />
                  Add Group
                </button>
              </div>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {accountGroups.map((group) => (
                  <div
                    key={group.id}
                    onClick={() => setSelectedGroup(group)}
                    className={`p-3 rounded cursor-pointer ${
                      selectedGroup?.id === group.id
                        ? "bg-indigo-100 border-2 border-indigo-600"
                        : "bg-gray-50 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{group.name}</p>
                        <p className="text-sm text-gray-600">{group.account_type}</p>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingGroup(group);
                            setGroupForm({
                              name: group.name,
                              account_type: group.account_type,
                              description: group.description || ""
                            });
                            setShowGroupModal(true);
                          }}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteGroup(group.id);
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Account Ledgers */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">
                  Account Ledgers
                  {selectedGroup && ` - ${selectedGroup.name}`}
                </h2>
                <button
                  onClick={() => {
                    setEditingLedger(null);
                    setLedgerForm({
                      ...ledgerForm,
                      group_id: selectedGroup?.id || ""
                    });
                    setShowLedgerModal(true);
                  }}
                  className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  disabled={!selectedGroup}
                >
                  <Plus size={16} className="inline mr-1" />
                  Add Ledger
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Name</th>
                      <th className="px-4 py-2 text-left">Code</th>
                      <th className="px-4 py-2 text-left">Module</th>
                      <th className="px-4 py-2 text-left">Opening Balance</th>
                      <th className="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLedgers.map((ledger) => (
                      <tr key={ledger.id} className="border-b">
                        <td className="px-4 py-2">{ledger.name}</td>
                        <td className="px-4 py-2">{ledger.code || "-"}</td>
                        <td className="px-4 py-2">{ledger.module || "-"}</td>
                        <td className="px-4 py-2">₹{ledger.opening_balance?.toFixed(2) || "0.00"}</td>
                        <td className="px-4 py-2">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                setEditingLedger(ledger);
                                setLedgerForm({
                                  name: ledger.name,
                                  code: ledger.code || "",
                                  group_id: ledger.group_id.toString(),
                                  module: ledger.module || "",
                                  description: ledger.description || "",
                                  opening_balance: ledger.opening_balance || 0,
                                  balance_type: ledger.balance_type,
                                  tax_type: ledger.tax_type || "",
                                  tax_rate: ledger.tax_rate?.toString() || "",
                                  bank_name: ledger.bank_name || "",
                                  account_number: ledger.account_number || "",
                                  ifsc_code: ledger.ifsc_code || "",
                                  branch_name: ledger.branch_name || ""
                                });
                                setShowLedgerModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteLedger(ledger.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Journal Entries Tab */}
        {activeTab === "journal-entries" && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Journal Entries</h2>
              <button
                onClick={() => setShowJournalModal(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                <Plus size={18} className="inline mr-2" />
                New Entry
              </button>
            </div>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Entry #</th>
                      <th className="px-4 py-2 text-left">Date</th>
                      <th className="px-4 py-2 text-left">Description</th>
                      <th className="px-4 py-2 text-left">Reference</th>
                      <th className="px-4 py-2 text-right">Amount</th>
                      <th className="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {journalEntries.map((entry) => (
                      <tr key={entry.id} className="border-b">
                        <td className="px-4 py-2">{entry.entry_number}</td>
                        <td className="px-4 py-2">
                          {new Date(entry.entry_date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-2">{entry.description}</td>
                        <td className="px-4 py-2">
                          {entry.reference_type && entry.reference_id
                            ? `${entry.reference_type} #${entry.reference_id}`
                            : "-"}
                        </td>
                        <td className="px-4 py-2 text-right">₹{entry.total_amount.toFixed(2)}</td>
                        <td className="px-4 py-2">
                          <button
                            onClick={() => {
                              // View entry details
                              alert(`Entry Details:\n${JSON.stringify(entry.lines, null, 2)}`);
                            }}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Trial Balance Tab */}
        {activeTab === "trial-balance" && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Trial Balance</h2>
              <button
                onClick={fetchTrialBalance}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Refresh
              </button>
            </div>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : trialBalance ? (
              <div>
                <div className="mb-4 flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {trialBalance.is_balanced ? (
                      <CheckCircle className="text-green-600" size={20} />
                    ) : (
                      <XCircle className="text-red-600" size={20} />
                    )}
                    <span className={`font-semibold ${trialBalance.is_balanced ? "text-green-600" : "text-red-600"}`}>
                      {trialBalance.is_balanced ? "Balanced" : "Not Balanced"}
                    </span>
                  </div>
                  <div className="text-gray-600">
                    Total Debits: ₹{trialBalance.total_debits.toFixed(2)} | 
                    Total Credits: ₹{trialBalance.total_credits.toFixed(2)}
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-2 text-left">Ledger Name</th>
                        <th className="px-4 py-2 text-right">Debit Total</th>
                        <th className="px-4 py-2 text-right">Credit Total</th>
                        <th className="px-4 py-2 text-right">Balance</th>
                        <th className="px-4 py-2 text-left">Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trialBalance.ledgers.map((ledger) => (
                        <tr key={ledger.ledger_id} className="border-b">
                          <td className="px-4 py-2">{ledger.ledger_name}</td>
                          <td className="px-4 py-2 text-right">₹{ledger.debit_total.toFixed(2)}</td>
                          <td className="px-4 py-2 text-right">₹{ledger.credit_total.toFixed(2)}</td>
                          <td className="px-4 py-2 text-right">
                            ₹{Math.abs(ledger.balance).toFixed(2)}
                            {ledger.balance < 0 && " (Cr)"}
                          </td>
                          <td className="px-4 py-2">{ledger.balance_type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">No data available</div>
            )}
          </div>
        )}

        {/* Account Group Modal */}
        {showGroupModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-xl font-bold mb-4">
                {editingGroup ? "Edit" : "Create"} Account Group
              </h3>
              <form onSubmit={handleCreateGroup}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Name</label>
                    <input
                      type="text"
                      value={groupForm.name}
                      onChange={(e) => setGroupForm({ ...groupForm, name: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Account Type</label>
                    <select
                      value={groupForm.account_type}
                      onChange={(e) => setGroupForm({ ...groupForm, account_type: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    >
                      <option value="Revenue">Revenue</option>
                      <option value="Expense">Expense</option>
                      <option value="Asset">Asset</option>
                      <option value="Liability">Liability</option>
                      <option value="Tax">Tax</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Description</label>
                    <textarea
                      value={groupForm.description}
                      onChange={(e) => setGroupForm({ ...groupForm, description: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      rows="3"
                    />
                  </div>
                </div>
                <div className="mt-6 flex space-x-3">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    {editingGroup ? "Update" : "Create"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowGroupModal(false);
                      setEditingGroup(null);
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Account Ledger Modal */}
        {showLedgerModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">
                {editingLedger ? "Edit" : "Create"} Account Ledger
              </h3>
              <form onSubmit={handleCreateLedger}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Name *</label>
                    <input
                      type="text"
                      value={ledgerForm.name}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, name: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Code</label>
                    <input
                      type="text"
                      value={ledgerForm.code}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, code: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Group *</label>
                    <select
                      value={ledgerForm.group_id}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, group_id: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    >
                      <option value="">Select Group</option>
                      {accountGroups.map((group) => (
                        <option key={group.id} value={group.id}>
                          {group.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Module</label>
                    <input
                      type="text"
                      value={ledgerForm.module}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, module: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="e.g., Booking, Purchase"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Opening Balance</label>
                    <input
                      type="number"
                      step="0.01"
                      value={ledgerForm.opening_balance}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, opening_balance: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Balance Type</label>
                    <select
                      value={ledgerForm.balance_type}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, balance_type: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="debit">Debit</option>
                      <option value="credit">Credit</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Tax Type</label>
                    <input
                      type="text"
                      value={ledgerForm.tax_type}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, tax_type: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="e.g., CGST, SGST, IGST"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Tax Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={ledgerForm.tax_rate}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, tax_rate: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Bank Name</label>
                    <input
                      type="text"
                      value={ledgerForm.bank_name}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, bank_name: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Account Number</label>
                    <input
                      type="text"
                      value={ledgerForm.account_number}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, account_number: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">IFSC Code</label>
                    <input
                      type="text"
                      value={ledgerForm.ifsc_code}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, ifsc_code: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Branch Name</label>
                    <input
                      type="text"
                      value={ledgerForm.branch_name}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, branch_name: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium mb-1">Description</label>
                    <textarea
                      value={ledgerForm.description}
                      onChange={(e) => setLedgerForm({ ...ledgerForm, description: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      rows="3"
                    />
                  </div>
                </div>
                <div className="mt-6 flex space-x-3">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    {editingLedger ? "Update" : "Create"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowLedgerModal(false);
                      setEditingLedger(null);
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Journal Entry Modal */}
        {showJournalModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Create Journal Entry</h3>
              <form onSubmit={handleCreateJournalEntry}>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Entry Date *</label>
                      <input
                        type="date"
                        value={journalForm.entry_date}
                        onChange={(e) => setJournalForm({ ...journalForm, entry_date: e.target.value })}
                        className="w-full border rounded px-3 py-2"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Description *</label>
                    <input
                      type="text"
                      value={journalForm.description}
                      onChange={(e) => setJournalForm({ ...journalForm, description: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Notes</label>
                    <textarea
                      value={journalForm.notes}
                      onChange={(e) => setJournalForm({ ...journalForm, notes: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      rows="2"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium">Journal Entry Lines *</label>
                      <button
                        type="button"
                        onClick={handleAddJournalLine}
                        className="px-3 py-1 bg-indigo-600 text-white rounded text-sm"
                      >
                        <Plus size={14} className="inline mr-1" />
                        Add Line
                      </button>
                    </div>
                    <div className="space-y-2">
                      {journalForm.lines.map((line, index) => (
                        <div key={index} className="grid grid-cols-12 gap-2 items-end border p-3 rounded">
                          <div className="col-span-4">
                            <label className="block text-xs font-medium mb-1">Debit Ledger</label>
                            <select
                              value={line.debit_ledger_id}
                              onChange={(e) => {
                                const newLines = [...journalForm.lines];
                                newLines[index].debit_ledger_id = e.target.value;
                                newLines[index].credit_ledger_id = ""; // Clear credit if debit selected
                                setJournalForm({ ...journalForm, lines: newLines });
                              }}
                              className="w-full border rounded px-2 py-1 text-sm"
                            >
                              <option value="">Select...</option>
                              {accountLedgers.map((ledger) => (
                                <option key={ledger.id} value={ledger.id}>
                                  {ledger.name}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="col-span-4">
                            <label className="block text-xs font-medium mb-1">Credit Ledger</label>
                            <select
                              value={line.credit_ledger_id}
                              onChange={(e) => {
                                const newLines = [...journalForm.lines];
                                newLines[index].credit_ledger_id = e.target.value;
                                newLines[index].debit_ledger_id = ""; // Clear debit if credit selected
                                setJournalForm({ ...journalForm, lines: newLines });
                              }}
                              className="w-full border rounded px-2 py-1 text-sm"
                            >
                              <option value="">Select...</option>
                              {accountLedgers.map((ledger) => (
                                <option key={ledger.id} value={ledger.id}>
                                  {ledger.name}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="col-span-3">
                            <label className="block text-xs font-medium mb-1">Amount *</label>
                            <input
                              type="number"
                              step="0.01"
                              value={line.amount}
                              onChange={(e) => {
                                const newLines = [...journalForm.lines];
                                newLines[index].amount = e.target.value;
                                setJournalForm({ ...journalForm, lines: newLines });
                              }}
                              className="w-full border rounded px-2 py-1 text-sm"
                              required
                            />
                          </div>
                          <div className="col-span-1">
                            {journalForm.lines.length > 1 && (
                              <button
                                type="button"
                                onClick={() => handleRemoveJournalLine(index)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <Trash2 size={16} />
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-6 flex space-x-3">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Create Entry
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowJournalModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}


