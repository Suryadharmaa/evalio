"use client";

import Image from "next/image";
import { sitePath } from "@/lib/site";
import { useState } from "react";
import { safeCollegeImageUrl, safeExternalUrl, safeInternalPath } from "@/lib/utils/safe-url";
import { cx } from "@/lib/utils/cx";
import styles from "./college-surfaces.module.css";

export interface CollegeMedia {
  id: string;
  media_type: string;
  image_url: string;
  source_url: string;
  license: string;
  attribution: string | null;
  alt_text: string;
  is_primary: boolean;
  width: number | null;
  height: number | null;
  sha256: string | null;
  content_type: string | null;
  verification_quality: string | null;
  trademark_notice: boolean | null;
  verified_at: string;
}

export function usableCampusMedia(media: CollegeMedia | null | undefined): boolean {
  const imageUrl = media?.media_type === "LOGO"
    ? safeInternalPath(media.image_url)
    : safeCollegeImageUrl(media?.image_url);
  return Boolean(media && imageUrl &&
    safeExternalUrl(media.source_url) && media.alt_text?.trim() && media.license &&
    media.license !== "UNKNOWN" && media.verified_at && !Number.isNaN(Date.parse(media.verified_at)));
}

export function CampusMedia({ media, name, location, hero = false, kind }: {
  media?: CollegeMedia | null;
  name: string;
  location: string;
  hero?: boolean;
  kind?: "campus" | "logo";
}) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const isLogo = media?.media_type === "LOGO";
  const imageUrl = usableCampusMedia(media)
    ? (isLogo ? safeInternalPath(media?.image_url) : safeCollegeImageUrl(media?.image_url))
    : null;
  const sourceUrl = safeExternalUrl(media?.source_url);
  const initials = name.split(/\s+/).filter(Boolean).slice(0, 2).map((word) => word[0]).join("");
  const fallbackKind = kind ?? (isLogo ? "logo" : "campus");
  return <figure className={cx(styles.media, hero && styles.heroMedia, isLogo && styles.logoMedia)}>
    <div className={styles.imageFrame}>
      {imageUrl && media && failedUrl !== imageUrl ? <Image
        alt={media.alt_text}
        className={cx(styles.campusImage, isLogo && styles.logoImage)}
        fill
        sizes={hero ? "(max-width: 1200px) 100vw, 1152px" : "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 384px"}
        src={isLogo ? sitePath(imageUrl) : imageUrl}
        preload={hero}
        unoptimized={isLogo}
        onError={() => setFailedUrl(imageUrl)}
      /> : <div className={styles.campusFallback}>
        <span className={styles.fallbackEyebrow}>EVALIO / COLLEGE DATA</span>
        <span aria-hidden="true" className={styles.initials}>{initials}</span>
        <span className={styles.fallbackLocation}>{location}</span>
        <span className={styles.fallbackNote}>{fallbackKind === "logo" ? "Verified logo not yet available" : "Campus image not yet available"}</span>
      </div>}
    </div>
    {imageUrl && media && !isLogo && failedUrl !== imageUrl ? <figcaption className={styles.imageCredit}>
      <span>{media.attribution ? `${media.attribution} · ` : ""}{media.license.replaceAll("_", " ")}</span>
      {sourceUrl ? <a href={sourceUrl} rel="noopener noreferrer" target="_blank">{isLogo ? "Logo source" : "Photo source"} <span aria-hidden="true">↗</span></a> : null}
    </figcaption> : null}
  </figure>;
}
