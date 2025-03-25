// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

// Define the schema using zod
const SiteSchema = z
  .object({
    name: z.string(),
    prefix: z.string(),
    location_id: z.number(),
    record_regime_recording_duration: z.number(),
    record_regime_pause_duration: z.number(),
    sample_rate: z.number(),
    remarks: z.string().optional().nullable()
  })
  .required({ name: true });

export default toTypedSchema(SiteSchema);

// Infer the TypeScript type from the schema
export type Site = z.infer<typeof SiteSchema>;
