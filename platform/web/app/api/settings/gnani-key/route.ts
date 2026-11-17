import { currentUser } from "@/lib/auth";
import { clearGnaniKey, gnaniKeyStatus, setGnaniKey } from "@/lib/users";

// The signed-in user's own Gnani API key. POST saves it (encrypted at rest with
// pgcrypto), DELETE removes it. The key never leaves the browser except to be
// stored; it is never read back out to the client.
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const user = await currentUser();
  if (!user) return Response.json({ error: "Please sign in." }, { status: 401 });

  let key = "";
  try {
    const body = (await request.json()) as { key?: unknown };
    key = String(body.key ?? "").trim();
  } catch {
    return Response.json({ error: "Bad request." }, { status: 400 });
  }
  if (key.length < 8 || key.length > 500) {
    return Response.json({ error: "That doesn't look like a Gnani API key." }, { status: 400 });
  }

  try {
    await setGnaniKey(user.id, key);
  } catch (error) {
    console.error("setGnaniKey failed:", error);
    return Response.json({ error: "Couldn't save the key. Please try again." }, { status: 500 });
  }
  return Response.json(await gnaniKeyStatus(user.id));
}

export async function DELETE() {
  const user = await currentUser();
  if (!user) return Response.json({ error: "Please sign in." }, { status: 401 });
  await clearGnaniKey(user.id);
  return Response.json(await gnaniKeyStatus(user.id));
}
