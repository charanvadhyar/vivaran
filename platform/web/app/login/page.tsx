import { redirect } from "next/navigation";
import { signInForDevelopment, signInWithGoogle } from "../actions";
import { Container } from "@/components/layout/Container";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Divider } from "@/components/ui/Divider";
import { Input } from "@/components/ui/Input";
import { currentUser, DEV_LOGIN } from "@/lib/auth";
import { BRAND } from "@/lib/brand";

export const metadata = { title: "Sign in" };

export default async function Login() {
  if (await currentUser()) redirect("/dashboard");
  return (
    <Container main narrow>
      <Card style={{ maxWidth: 440, margin: "32px auto" }} title={`Sign in to ${BRAND.name}`}
        subtitle="You need an account to make videos. Watching is open to everyone.">
        <form action={signInWithGoogle}>
          <Button type="submit" variant="primary" size="lg" block>Continue with Google</Button>
        </form>
        {DEV_LOGIN ? (
          <>
            <Divider label="development" />
            <Alert tone="note">Development sign-in is on. Turn it off (DEV_LOGIN=0) before anyone else can reach this site.</Alert>
            <form action={signInForDevelopment} style={{ display: "grid", gap: 10, marginTop: 12 }}>
              <Input name="name" label="Any name" placeholder="Asha Rao" required maxLength={40} />
              <Button type="submit">Sign in without Google</Button>
            </form>
          </>
        ) : null}
      </Card>
    </Container>
  );
}
