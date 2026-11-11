import NextAuth, { type NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import { WAITLIST } from "./mode";
import { upsertUser, userById, type User } from "./users";

const devLogin = process.env.DEV_LOGIN === "1";

const providers: NextAuthConfig["providers"] = [Google];
if (devLogin) {
  // For testing on your own machine without Google. Never enable on a public server.
  providers.push(
    Credentials({
      id: "dev",
      name: "Development sign-in",
      credentials: { name: { label: "Name" } },
      authorize: async (input) => {
        const name = String(input?.name ?? "").trim().slice(0, 40);
        if (!name) return null;
        const user = await upsertUser({ sub: `dev:${name.toLowerCase()}`, email: `${name.toLowerCase()}@dev.local`, name });
        return { id: user.id, name: user.name, email: user.email };
      },
    }),
  );
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers,
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
  callbacks: {
    // On sign-in, find or create the account and remember its id in the session.
    async jwt({ token, account, profile, user }) {
      if (account?.provider === "google" && profile?.sub) {
        const saved = await upsertUser({
          sub: profile.sub,
          email: profile.email ?? "",
          name: profile.name ?? profile.email ?? "Creator",
          image: (profile.picture as string | undefined) ?? null,
          verified: profile.email_verified === true,
        });
        token.uid = saved.id;
      } else if (account?.provider === "dev" && user?.id) {
        token.uid = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (token.uid) (session as { uid?: string }).uid = token.uid as string;
      return session;
    },
  },
});

export const DEV_LOGIN = devLogin;

/** The signed-in account, or null. */
export async function currentUser(): Promise<User | null> {
  if (WAITLIST) return null;
  const session = await auth();
  const uid = (session as { uid?: string } | null)?.uid;
  return uid ? userById(uid) : null;
}
