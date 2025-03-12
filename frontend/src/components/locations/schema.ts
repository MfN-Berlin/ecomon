// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

// Define the schema using zod
const locationSchema = z.object({
  name: z.string(),
  lat: z.number().min(-90).max(90).optional().nullable(),
  long: z.number().min(-180).max(180).optional().nullable(),
  remarks: z.string().optional().nullable()
});

export default toTypedSchema(locationSchema);

// Infer the TypeScript type from the schema
export type Location = z.infer<typeof locationSchema>;
