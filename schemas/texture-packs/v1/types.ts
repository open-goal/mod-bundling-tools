/**
 * Semantic Version
 * @pattern ^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
 */
type Semver = string;

type SupportedGame = "jak1" | "jak2" | "jak3" | "jakx";

type ValidTags =
  | "enhancement"
  | "overhaul"
  | "highres"
  | "parody"
  | "themed"
  | "mods"
  | string;

export interface TexturePackMetadata {
  schemaVersion: Semver;
  version: Semver;
  name: string;
  description: string;
  authors: string;
  publishedDate: string;
  tags: ValidTags[];
  supportedGames: SupportedGame[];
}
