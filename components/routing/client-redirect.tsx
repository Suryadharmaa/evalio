"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function ClientRedirect({ to, preserveCollege = false }: { to: string; preserveCollege?: boolean }) {
  const router = useRouter();
  const query = useSearchParams();
  const college = preserveCollege ? query.get("college") : null;
  const destination = college ? `${to}?college=${encodeURIComponent(college)}` : to;
  useEffect(() => { router.replace(destination); }, [destination, router]);
  return <p role="status" className="site-container py-16">Opening the tool… <Link className="quiet-link" href={destination}>Continue</Link></p>;
}
