"use client";

import { useRouter } from "next/navigation";

type Props = {
  currentSeason: string;
  seasons: string[];
};

export function TeamDirectorySelect({
  currentSeason,
  seasons,
}: Props) {
  const router = useRouter();

  return (
    <label className="frl-context-control frl-context-control-season">
      <span>Season</span>
      <select
        aria-label="Premier League season"
        value={currentSeason}
        onChange={(event) => {
          router.push(
            `/teams?season=${encodeURIComponent(event.target.value)}`
          );
        }}
      >
        {seasons.map((season) => (
          <option key={season} value={season}>
            {season}
          </option>
        ))}
      </select>
      <span className="frl-context-chevron">?</span>
    </label>
  );
}
