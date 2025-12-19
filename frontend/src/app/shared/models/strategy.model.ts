export interface Strategy {
  id: number;
  name: string;
  description?: string;
  code_ref: string;
  default_parameters: Record<string, any>;
}
