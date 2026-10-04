import Link from "next/link";

import { recordPath } from "@/lib/site";
import { StatusBadge } from "@/components/ui/status-badge";
import { CampusMedia, type CollegeMedia } from "./campus-media";
import { collegeLabel } from "./college-format";
import styles from "./college-surfaces.module.css";

export interface CollegeSummary {
  id: string;
  slug: string;
  name: string;
  country_code: string;
  state_region: string | null;
  city: string | null;
  institution_type: string | null;
  identity_confidence: string | null;
  application_platform_primary: string | null;
  application_platforms: string[];
  official_website: string | null;
  test_policy: string | null;
  need_policy: string | null;
  primary_media: CollegeMedia | null;
}

export function CollegeCard({ college }: { college: CollegeSummary }) {
  const location = [college.city, college.state_region, college.country_code].filter(Boolean).join(" · ");
  return <article className={styles.collegeCard}>
    <CampusMedia kind="logo" location={location} media={college.primary_media} name={college.name} />
    <div className={styles.cardBody}>
      <p className={styles.cardType}>{collegeLabel(college.institution_type)}</p>
      <h3 className={styles.cardName}><Link href={recordPath("colleges", college.slug)}>{college.name}</Link></h3>
      <p className={styles.cardLocation}>{location || "Location not yet verified"}</p>
      <dl className={styles.cardFacts}>
        <div><dt>Testing</dt><dd>{collegeLabel(college.test_policy)}</dd></div>
        <div><dt>International aid</dt><dd>{collegeLabel(college.need_policy)}</dd></div>
      </dl>
      <div className={styles.cardProvenance}>
        {college.identity_confidence && college.identity_confidence !== "UNKNOWN" ? <StatusBadge tone="info">{college.identity_confidence} identity confidence</StatusBadge> : <StatusBadge>Verification varies by field</StatusBadge>}
        <span>Source dates in profile</span>
      </div>
      <Link aria-label={`Explore ${college.name}`} className={styles.cardLink} href={recordPath("colleges", college.slug)}>
        Explore college <span aria-hidden="true">→</span>
      </Link>
    </div>
  </article>;
}
