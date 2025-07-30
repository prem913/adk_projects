import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface TransactionStatsProps {
  initiated: number;
  inProgress: number;
  completed: number;
  failed: number;
}

export function TransactionStats({
  initiated,
  inProgress,
  completed,
  failed,
}: TransactionStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Initiated</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{initiated}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">In Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{inProgress}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-500">{completed}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Failed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-500">{failed}</div>
        </CardContent>
      </Card>
    </div>
  );
}
