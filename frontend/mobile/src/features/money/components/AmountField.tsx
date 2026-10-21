import { TextField } from '@/shared/components/TextField';

type Props = {
  label: string;
  value: string;
  onChange: (text: string) => void;
  hint?: string;
  error?: string;
};

/** Rand typed as the student would ("1500", "48.50"); the screen turns it into cents with parseRand. */
export function AmountField({ label, value, onChange, hint, error }: Props) {
  return (
    <TextField
      label={label}
      value={value}
      onChangeText={(text) => onChange(text.replace(/[^0-9.,\sR]/gi, '').slice(0, 14))}
      keyboardType="decimal-pad"
      placeholder="0"
      hint={hint}
      error={error}
    />
  );
}
