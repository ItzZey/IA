import type { NextApiRequest, NextApiResponse } from "next";
import { analyzeTicker } from "@/lib/finance";

type ErrorResponse = {
  error: string;
};

export default async function handler(request: NextApiRequest, response: NextApiResponse) {
  const ticker = Array.isArray(request.query.ticker) ? request.query.ticker[0] : request.query.ticker || "TTE.PA";

  try {
    const result = await analyzeTicker(ticker);
    response.status(200).json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erreur inconnue";
    response.status(502).json({ error: message } satisfies ErrorResponse);
  }
}
