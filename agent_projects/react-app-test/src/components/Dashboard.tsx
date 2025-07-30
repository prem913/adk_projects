import { useState, useEffect } from "react";
import { BranchSelector } from "./BranchSelector";
import { TimePicker } from "./TimePicker";
import { TransactionStats } from "./TransactionStats";

// Mock data fetching function
const fetchTransactionData = (branch: string, time: string) => {
  console.log(`Fetching data for branch: ${branch}, time: ${time}`);
  // In a real app, you would make an API call here.
  // For now, we'll return some mock data.
  const data = {
    tw: {
      "1h": { initiated: 120, inProgress: 30, completed: 85, failed: 5 },
      "3h": { initiated: 350, inProgress: 90, completed: 250, failed: 10 },
      "1d": { initiated: 1500, inProgress: 200, completed: 1250, failed: 50 },
      "30d": {
        initiated: 45000,
        inProgress: 1500,
        completed: 42000,
        failed: 1500,
      },
    },
    kr: {
      "1h": { initiated: 100, inProgress: 25, completed: 70, failed: 5 },
      "3h": { initiated: 300, inProgress: 80, completed: 210, failed: 10 },
      "1d": { initiated: 1300, inProgress: 180, completed: 1100, failed: 40 },
      "30d": {
        initiated: 40000,
        inProgress: 1300,
        completed: 38000,
        failed: 1300,
      },
    },
    jp: {
      "1h": { initiated: 80, inProgress: 20, completed: 55, failed: 5 },
      "3h": { initiated: 250, inProgress: 70, completed: 170, failed: 10 },
      "1d": { initiated: 1100, inProgress: 150, completed: 900, failed: 30 },
      "30d": {
        initiated: 35000,
        inProgress: 1100,
        completed: 33000,
        failed: 1100,
      },
    },
  };
  return data[branch as keyof typeof data][
    time as keyof typeof data[keyof typeof data]
  ];
};

export function Dashboard() {
  const [branch, setBranch] = useState("tw");
  const [time, setTime] = useState("1h");
  const [stats, setStats] = useState({
    initiated: 0,
    inProgress: 0,
    completed: 0,
    failed: 0,
  });

  useEffect(() => {
    const data = fetchTransactionData(branch, time);
    setStats(data);
  }, [branch, time]);

  return (
    <div className="flex-col md:flex">
      <div className="border-b">
        <div className="flex h-16 items-center px-4">
          <h1 className="text-3xl font-bold tracking-tight">Ops Dashboard</h1>
          <div className="ml-auto flex items-center space-x-4">
            <BranchSelector onBranchChange={setBranch} />
            <TimePicker onTimeChange={setTime} />
          </div>
        </div>
      </div>
      <div className="flex-1 space-y-4 p-8 pt-6">
        <TransactionStats {...stats} />
      </div>
    </div>
  );
}
