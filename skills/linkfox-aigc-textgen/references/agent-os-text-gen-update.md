# AgentOS 生文说明与内置专家更新交接

- 来源：linkfox-skills-repository master e34f1f90、agentstudio-skill master 2e0a7bc1；均在独立feature分支修改，提交/推送状态以分支Git记录及本次交付为准；未合并或发布。
- 权威源：skills/linkfox-aigc-textgen；更新模型码、参数、计费说明、示例和安全恢复查询。experts中48份内嵌依赖与1份独立生文专家同步配套文档和运行文件，保留各自_meta版本/发布状态及父专家业务提示词。Listing专家内嵌版本的差异仅为旧上传说明缺失，本次补齐其可运行依赖，不改Listing业务。
- 内置专家：agentstudio-skill仅改agents下路由器媒体索引和视频复刻专家的能力边界；LF_GEM_2的medium/low调用、已明确传旧Flash的有效调用保持兼容，不为迁移强制换模型或增加费用。agentstudio-skill/linkfoxagent-v2以及全局CLAUDE规则均未修改。
- 视频：不删旧原生视频流程；其前提是确认旧入口能力。新标准生文不接受原生视频/音频时沿用既有抽帧流程，缺少音轨/口播信息不能由图片臆造。
- 发布展示登记：skills-version.json只更新生文和生文专家的description/desc四处文案；没有改版本、newVersion、发布渠道状态、收费数字或密钥。
- 发布：由人工将相应feature合并master后，通知林鄂伟按既有发布/依赖同步流程操作，再同步到agentstudio-skill/linkfoxagent-v2。此次未运行publish脚本、未触发CI/CD、未给外部发消息。
- 环境：新7模型和新实扣字段以AI/工具部署及实际模型开通为准；新版接口新建任务统一走AI生文计费，技能不靠换模型或重建任务探测可用性。不可将新任务查询不收费承诺套到旧任务。
- 验证：离线契约测试覆盖请求透传、只查询恢复、一次创建、超时恢复、有限重试、费用字段/异常保留、旧费用不重算，以及专家包自包含。未调用真实模型或计费接口。

## 本地验证结果

- 新增生文契约测试19项全部通过；包括49个专家包位点的文件一致性、自包含导入和Python语法检查。
- 根目录全量执行94项时，已有生图/视频测试报58个导入错误及1个函数哈希基线不一致；在隔离目录导出未改动master原始文件，分别复现了_linkfox_transport导入失败与相同的生图函数哈希失败。没有放宽原断言或修改这些无关模块。
- 全量日志：工作区.validation/skills-textgen-tests.log；master复现：skills-master-baseline-imports.log、skills-master-baseline-hash.log。不能把本次结果描述成仓库全量测试通过。
- 格式校验保留原有CRLF文件，以cr-at-eol检查换行；不改Git全局/仓库配置。

## 2026-11-10 配套调整

- 配套 AI 与工具代码移除生文计费开关；部署新版后，所有新建任务（含默认模型和旧别名）统一走收费创建，旧 TEXT 任务仍按持久化类型查询及历史计价。
- 同步主 Skill 与49份专家包的模型可用性说明，不再要求配置计费开关；实际部署、模型价格与环境开通仍须单独确认。
- 未直接修改 agentstudio-skill/linkfoxagent-v2，仍由既有人工同步流程处理。
