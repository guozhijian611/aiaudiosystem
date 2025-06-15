export interface FormOptionList {
  type: string;
  prop: string;
  placeholder: string;
  activeValue?: string;
  opts?: Array<{ label: string; value: string }>;
}

export interface FormOption {
  labelWidth: string;
  span: number;
  list: Array<{
    type: string;
    label: string;
    prop: string;
    required: boolean;
  }>;
}

export interface User {
  id?: number;
  name?: string;
  password?: string;
  email?: string;
  phone?: string;
  role?: string;
  date?: string;
} 