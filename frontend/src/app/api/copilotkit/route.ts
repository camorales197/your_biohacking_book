import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  OpenAIAdapter,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const runtime = new CopilotRuntime({
  remoteEndpoints: [],
});

// NOTA: Using OpenAIAdapter as a placeholder; CopilotKit sidebar uses the model
// configured in the runtime. The book generation itself uses the FastAPI backend.
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new OpenAIAdapter({
      openai: undefined as never,
    }),
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};
