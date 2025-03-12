// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

// Define the schema using zod
const modelSchema = z.object({
  name: z.string(),
  endpoint: z.string(),
  short_name: z.string(),
  remarks: z.string().optional().nullable()
});

export default toTypedSchema(modelSchema);
// Infer the TypeScript type from the schema
export type Model = z.infer<typeof modelSchema>;
