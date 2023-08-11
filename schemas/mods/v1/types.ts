// interface ChangelogEntry {
//     summary: string,
//     timestamp: string,
//     authors?: string[],
//     description?: string,
// }

/**
 * Semantic Version
 * @pattern ^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
 */
type Semver = string;

type SupportedGame = "jak1" | "jak2" | "jak3" | "jakx";

type ValidTags =
  | "beta"
  | "challenge"
  | "custom-enemy"
  | "custom-level"
  | "gameplay-mod"
  | "multiplayer"
  | "practice"
  | "rng"
  | "speedrunning"
  | "texture-mod";

export interface ModMetadata {
  schemaVersion: Semver;
  version: Semver;
  name: string;
  description: string;
  authors: string[];
  // changelog: ChangelogEntry[], TODO eventually
  tags: ValidTags[];
  publishedDate: string;
  websiteUrl?: string;
  supportedGames: SupportedGame[];
}
