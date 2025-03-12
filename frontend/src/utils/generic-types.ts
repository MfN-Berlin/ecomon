export type WithMeta<T> = T & {
  created_at: string;
  updated_at: string;
  id?: number;
};

export type WithId<T> = T & {
  id?: number;
};

export type FormProps<T> = {
  data?: WithMeta<T>;
  cancelLabel?: string;
  okLabel?: string;
  loading?: boolean;
};
