import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function TimePicker({
  onTimeChange,
}: {
  onTimeChange: (time: string) => void;
}) {
  return (
    <Select onValueChange={onTimeChange} defaultValue="1h">
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select Time Range" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="1h">Last 1hr</SelectItem>
        <SelectItem value="3h">Last 3hrs</SelectItem>
        <SelectItem value="1d">Last 1 day</SelectItem>
        <SelectItem value="30d">Last 30 days</SelectItem>
      </SelectContent>
    </Select>
  );
}
