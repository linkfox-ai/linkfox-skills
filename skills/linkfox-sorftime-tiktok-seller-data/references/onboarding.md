# LinkFox authorization and billing help

Run `python scripts/onboarding.py` to check whether a LinkFox API key is configured; it prints no key value and makes no network request.

- Missing key: guide the user to [LinkFox key setup](https://skill.linkfox.com/linkfoxskills/guide.htm). Set `LINKFOX_AGENT_API_KEY` or legacy `LINKFOXAGENT_API_KEY`, then start a new session if the environment has not refreshed.
- LinkFox authorization failure: verify the environment and gateway address; never print or include a key in feedback.
- LinkFox insufficient credits: direct the user to [LinkFox](https://agent.linkfox.com/) to inspect their account and available plans. This skill does not automatically register users, send verification codes, create orders or initiate payments.
- Sorftime upstream quota/access failure: this belongs to the service operator. Do not tell the end user to configure a Sorftime key or purchase a Sorftime plan to use the LinkFox skill.
