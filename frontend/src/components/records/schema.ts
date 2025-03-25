// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

const modelSchema = z.object({
  site_id: z.number(),
  filepath: z.string(),
  filename: z.string(),
  record_datetime: z.date(),
  duration: z.number(),
  channels: z.string(),
  sample_rate: z.number(),
  mime_type: z.string(),
  errors: z.string().optional().nullable()
});

export default toTypedSchema(modelSchema);
// Infer the TypeScript type from the schema
export type Model = z.infer<typeof modelSchema>;
