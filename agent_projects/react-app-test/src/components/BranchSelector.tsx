import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function BranchSelector({
  onBranchChange,
}: {
  onBranchChange: (branch: string) => void;
}) {
  return (
    <Select onValueChange={onBranchChange} defaultValue="tw">
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select Branch" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="tw">Taiwan</SelectItem>
        <SelectItem value="kr">Korea</SelectItem>
        <SelectItem value="jp">Japan</SelectItem>
      </SelectContent>
    </Select>
  );
}
