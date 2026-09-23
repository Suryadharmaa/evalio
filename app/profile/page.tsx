import { ProfileEditor } from "@/components/profile/profile-editor";
import { ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function ProfilePage() {
  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-12 sm:px-8 lg:px-12">
      <p className="text-sm font-semibold text-primary">Applicant profile</p>
      <h1 className="mt-2 text-4xl font-bold tracking-tight">Set up your context</h1>
      <p className="mt-3 max-w-2xl leading-7 text-muted">
        Evalio preserves your curriculum and grading system. It will not force international grades into a US 4.0 GPA.
      </p>
      <ProfileEditor />
      <Card className="mt-8 p-6">
        <h2 className="text-xl font-bold">Continue profile setup</h2>
        <div className="mt-5 flex flex-wrap gap-3">
          <ButtonLink href="/profile/academics" variant="secondary">Academics</ButtonLink>
          <ButtonLink href="/profile/testing" variant="secondary">Testing</ButtonLink>
          <ButtonLink href="/profile/activities" variant="secondary">Activities</ButtonLink>
          <ButtonLink href="/profile/honors" variant="secondary">Honors</ButtonLink>
          <ButtonLink href="/essays" variant="secondary">Essays</ButtonLink>
          <ButtonLink href="/recommendations" variant="secondary">Recommendations</ButtonLink>
        </div>
      </Card>
    </div>
  );
}
