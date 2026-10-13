// ESLint flat config：守 24.2 节约定——组件里不得硬编码颜色，颜色只用 src/tokens.css 的语义令牌。
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**", "e2e/**", "node_modules/**"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: { "react-hooks": reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "no-restricted-syntax": [
        "error",
        {
          selector: "Literal[value=/^#[0-9a-fA-F]{3,8}$/]",
          message: "禁止硬编码颜色，请使用 tokens.css 的语义令牌（见 AGENTS.md 前端约定）",
        },
      ],
    },
  },
);
