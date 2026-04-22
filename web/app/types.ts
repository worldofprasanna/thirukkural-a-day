// Shape of /content/kurals/{id}.json. Source of truth lives in CLAUDE.md + pipeline/story.py.
// If you change the JSON schema in the pipeline, update this file in the same commit.

export type Character = {
  name: string;
  description: string;
};

export type Panel = {
  beat: string;
  scene: string;
};

export type Kural = {
  id: number;
  chapter: string;
  theme: string;
  tamil: string;
  translation: string;
  moral: string;
  title: string;
  story: string[];
  moral_line: string;
  characters: Character[];
  panels: Panel[];
};
