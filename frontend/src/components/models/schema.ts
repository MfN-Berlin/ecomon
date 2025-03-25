// types.ts
import { z } from "zod";

import { toTypedSchema } from "@vee-validate/zod";

// Define the schema using zod
const modelSchema = z.object({
  name: z.string(),
  additional_docker_arguments: z.string().optional().nullable(),
  additional_model_arguments: z.string().optional().nullable(),
  segment_duration: z.number().optional().nullable(),
  step_duration: z.number().optional().nullable(),
  remarks: z.string().optional().nullable()
});

export default toTypedSchema(modelSchema);
// Infer the TypeScript type from the schema
export type Model = z.infer<typeof modelSchema>;
