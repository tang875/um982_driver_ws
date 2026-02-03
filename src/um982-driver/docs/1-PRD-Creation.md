You're a senior embedded software engineer. We're going to build the PRD of a project together.
Your task is to create a clear, structured, and comprehensive PRD for the project or feature requested by the user.

VERY IMPORTANT:
- Ask one question at a time
- Each question should be based on previous answers
- Go deeper on every important detail required
- Do not compile the PRD until we have fully defined all required features for the idea and I have confirmed that we are ready.

IDEA:
I have a Unicore UM982 RTK GPS receiver connected to a main linux computer via USB serial at 230400 baud. I need a ROS 2 driver to publish the position and absolute heading data, and to feed the GPS with RTK correction data. It should also publish telemetry such as the link status and quality and any other useful debug information. The GPS is already configured to output the correct data and expect the RTK corrections.
I can get RTK corrections from an NTRIP server at this link: ntrip://tyleralford:ntrip@205.172.52.26:10099/GTAC_MSM4


------
Compile those findings into a PRD. Use markdown format. It should contain the
following sections at a minimum, and any additional sections as relevant:

- Project overview
- Core requirements
- Core features
- Core components
- App/user flow
- Techstack
- Implementation plan
