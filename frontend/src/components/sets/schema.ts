// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

// Define the schema using zod
const SetSchema = z
  .object({
    name: z.string(),
    remarks: z.string().optional().nullable()
  })
  .required({ name: true });

export default toTypedSchema(SetSchema);

// Infer the TypeScript type from the schema
export type Set = z.infer<typeof SetSchema>;
