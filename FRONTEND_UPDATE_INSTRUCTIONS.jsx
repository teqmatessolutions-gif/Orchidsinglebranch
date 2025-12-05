// UPDATED DEPARTMENT CARD COMPONENT
// Replace lines 969-977 in Account.jsx with this code:

{/* Expenses Breakdown */ }
<div className="pt-2 border-t border-gray-100">
    <p className="text-xs font-semibold text-gray-500 mb-2">EXPENSES</p>
    <div className="space-y-1">
        <div className="flex items-center justify-between pl-2">
            <span className="text-xs text-gray-600 flex items-center gap-1">
                <FileText className="text-orange-400 w-3 h-3" />
                Regular Expenses
            </span>
            <span className="text-sm font-semibold text-orange-600">
                ₹<CountUp end={data.regular_expenses || 0} duration={1.5} decimals={2} separator="," />
            </span>
        </div>
        <div className="flex items-center justify-between pl-2">
            <span className="text-xs text-gray-600 flex items-center gap-1">
                <Package className="text-red-400 w-3 h-3" />
                Inventory Consumed
            </span>
            <span className="text-sm font-semibold text-red-600">
                ₹<CountUp end={data.inventory_consumption || 0} duration={1.5} decimals={2} separator="," />
            </span>
        </div>
        <div className="flex items-center justify-between pl-2">
            <span className="text-xs text-gray-600 flex items-center gap-1">
                <ShoppingCart className="text-purple-400 w-3 h-3" />
                Capital Investment
            </span>
            <span className="text-sm font-semibold text-purple-600">
                ₹<CountUp end={data.capital_investment || 0} duration={1.5} decimals={2} separator="," />
            </span>
        </div>
    </div>
</div>

// INSTRUCTIONS:
// 1. Open c:\releasing\orchid\dasboard\src\pages\Account.jsx
// 2. Find lines 969-977 (the single "Expenses" div)
// 3. Replace with the code above
// 4. Save the file
// 5. The frontend will hot-reload and show the breakdown
