import { Container } from "@/components/layout/Container";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

export default function NotFound() {
  return (
    <Container main narrow>
      <EmptyState icon="search" title="There is nothing at this address"
        text="The video may be private, or the link may be wrong." action={<Button href="/" variant="primary">Go to the home page</Button>} />
    </Container>
  );
}
