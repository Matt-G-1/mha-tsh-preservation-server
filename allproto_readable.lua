-- allproto_bytecode.lua — protocol schemas
-- 1744 schemas recovered

-- === achieveinfo ===
  id: number
  status: byte
  curvalue: number
  finishtime: number

-- === area_event_hero_info ===
  HeroUId: number
  MoveValue: number
  Pos: number [repeated]

-- === area_event_stage_data ===
  StageId: number
  PassedTimes: number
  DropCountTimes: number
  Star: byte

-- === area_event_stage_times ===
  StageId: number
  FightTimes: number
  ResetTimes: number

-- === attached_card_reform_info ===
  Uid: number
  ReformInfo: {  [repeated]
    Index: number
    Val: number
  }

-- === attribute_string_info ===
  key: string
  value: number

-- === base_station_info ===
  iBaseStationId: byte
  iLevel: byte
  iFinishTaskCount: number
  iFinishEntrustTaskCount: number

-- === battlefield_task ===
  Index: byte
  TaskId: number
  Pro: byte
  State: byte

-- === campaign_hero_info ===
  HeroUId: number
  Tiredness: number
  Damage: number
  FightCount: number

-- === campaign_pos ===
  SceneId: number
  Pos: number [repeated]

-- === campaign_task_info ===
  Id: number
  Status: number
  Cond: {  [repeated]
    CompCount: number
  }

-- === card_seeinfo ===
  Uid: number
  HeroId: dword
  Lv: word
  Exp: number
  ShapeId: number
  FashionId: number
  Fighting: number
  Satiety: number
  WorkoutLv: byte
  WorkoutItem: byte [repeated]
  ResonateLv: byte
  ResonatePiece: byte [repeated]
  IsLock: byte
  IsLockSkill: byte [repeated]
  SupportSkills: {  [repeated]
    Index: number
    HeroCId: number
  }
  FameLv: word
  FameExp: number

-- === climbing ===
  IsClimbing: byte
  ClimbMoveDir: number
  Normal: {
    X: number
    Y: number
    Z: number
  }

-- === commentinfo ===
  CommentIdx: number
  SenderUid: number
  SenderInfo: {
    Uid: number
    Name: string
    AvatarId: byte
    AvatarFrameId: byte
  }
  Content: string
  LikeNum: number
  ReplyNum: number
  SendTime: number

-- === commentinfoex ===
  CommentIdx: number
  SenderUid: number
  SenderInfo: {
    Uid: number
    Name: string
    AvatarId: byte
    AvatarFrameId: byte
  }
  Content: string
  LikeNum: number
  ReplyNum: number
  SendTime: number
  IsLike: number

-- === crosspvp_pos ===
  FormationId: byte
  Pos: byte
  HeroCId: number
  Fighting: number

-- === custom_gift ===
  Id: number
  BuyTime: number
  TriggerTime: number
  TriggerCount: byte
  BuyCount: byte
  Cond: number [repeated]

-- === egginfo ===
  EType: number
  State: byte
  Progress: byte
  ExtraKey: string [repeated]
  ExtraVal: number [repeated]

-- === emergency_event ===
  Uid: number
  StageId: number
  StartTime: number
  Lv: number

-- === entrust_task_data ===
  TaskUniqId: number
  TaskId: number
  StartTime: dword
  CardUidList: number [repeated]

-- === equip_attr_info ===
  Uid: number
  ExtraAttr: {  [repeated]
    Id: number
    Value: string
  }
  HideAttr: {  [repeated]
    Id: number
    Value: number
  }

-- === extra_item_data ===
  ItemId: number
  Num: number
  Extra: number

-- === friendinfo ===
  HostId: number
  Uid: number
  Name: string
  Level: number
  TopLevel: number
  FaceIcon: number
  FaceFrame: number
  Time: dword
  OnLine: number
  LeaveTime: number
  QinMi: number
  StrengthStatus: byte
  Tag: byte

-- === furniture_produce ===
  FurnitureId: number
  FurnitureUid: number
  FinishFlag: byte
  TimePoint: number

-- === group_hero_info ===
  HeroUid: number
  HeroId: number
  Level: byte
  Fighting: number
  JoinTimes: byte

-- === group_invite_info ===
  HostId: number
  WanFaId: number
  GroupId: number
  LeaderUid: number
  LeaderName: string
  LeaderLevel: byte
  LeaderTopLevel: number
  LeaderFaceIcon: number
  LeaderFaceFrame: number
  MemberAmount: byte
  IntExtra: number [repeated]
  StrExtra: string [repeated]

-- === group_map_data ===
  StageId: number
  TeamList: number [repeated]
  Tag: number
  IsDoor: number
  Status: number
  TransTime: number
  RepairTime: number

-- === group_member_base_info ===
  SvrId: number
  Uid: number
  Name: string
  Level: number
  TopLevel: number
  FaceIcon: number
  FaceFrame: number
  HeroUse: number
  GroupFinishTimes: number
  DayFinishTimes: number
  WeekFinishTimes: number
  HeroList: group_hero_info [repeated]

-- === group_member_data ===
  Uid: number
  Name: string
  SvrId: number
  HeroId: number
  Pos: number
  Pass: number
  Damage: number
  Status: number
  DieRecover: number
  EatBuff: number

-- === group_member_info ===
  BaseInfo: group_member_base_info
  ReadyStatus: byte

-- === hero_gem_data ===
  HeroCId: number
  GemData: {  [repeated]
    SkillId: number
    UUids: number [repeated]
  }

-- === home_checkin_list ===
  Floor: number
  RoleId: number [repeated]

-- === home_floor_furniture ===
  Floor: number
  Decoration: number [repeated]
  Furniture: home_furniture [repeated]

-- === home_furniture ===
  Uid: number
  FurnitureId: number
  X: number
  Y: number
  Z: number
  Face: number
  WallIndex: number

-- === home_liker ===
  Uid: number
  Name: string
  AvatarId: dword
  AvatarFrameId: dword
  Level: dword
  TopLevel: number
  Online: byte
  Liker: dword
  Time: number

-- === home_people_data ===
  RoleId: number
  MoodValue: number

-- === home_proof_task_status ===
  TaskId: number
  TaskStatus: number
  CurValue: number

-- === home_role_event ===
  RoleId: number
  EventIndex: number
  EventTimePoint: number

-- === home_role_mood ===
  RoleId: number
  Mood: number
  AutoRiseFlag: byte
  MoodTimePoint: number

-- === item_data ===
  ItemId: number
  Num: number

-- === item_param ===
  NumberList: {  [repeated]
    id: number
    value: number
  }
  StringList: {  [repeated]
    id: number
    value: string
  }

-- === league_pvp_base_info ===
  LeagueId: number
  LeagueName: string
  LeagueLv: number
  LeagueIcon: number
  LeagueFrameIcon: number
  LeagueOnlineCount: number
  LeagueMemberAmount: number
  LeagueAd: string
  PvpScore: number
  PvpRank: number

-- === league_pvp_cd_data ===
  Uid: number
  FightStatus: number
  ProtectCD: number
  ReliveCD: number

-- === league_pvp_fight_data ===
  Uid: number
  Name: string
  FaceIcon: number
  FaceFrame: number
  Camp: number

-- === league_pvp_hero_data ===
  Uid: number
  HeroCId: number
  MaxHp: number
  Hp: number
  BuffLayer: number
  CdTime: number

-- === league_pvp_member_fight_data ===
  Camp: number
  Uid: number
  Name: string
  HeroId: number
  BattleLog: number [repeated]
  Damage: number
  LeagueName: string
  SvrId: number

-- === league_pvp_member_record ===
  Uid: number
  Name: string
  FaceIcon: number
  FaceFrame: number
  Job: number
  Fighting: number
  PvpCount: number
  KillCount: number
  Online: number
  ActiveStar: number
  LogoutTime: number

-- === league_pvp_mvp_data ===
  LeagueId: number
  Name: string
  Level: number
  FaceIcon: number
  FaceFrame: number
  BattleLog: number [repeated]

-- === league_pvp_record ===
  SvrId: number
  LeagueId: number
  LeagueName: string
  LeagueIcon: number
  LeagueFrameIcon: number
  IsWin: number
  StartScore: number [repeated]
  Kills: number [repeated]
  OverScore: number
  Time: number

-- === league_pvp_report ===
  Id: number
  Camp: number
  SList: string [repeated]

-- === league_pvp_resource_data ===
  ResourceId: number
  Score: number
  CampList: number [repeated]
  OccupyList: number [repeated]

-- === league_pvp_result ===
  Camp: number
  LeagueId: number
  LeagueName: string
  OverScore: number
  TotalKill: number
  ResourceTotal: number
  AddScore: number

-- === league_pvp_scene_data ===
  Camp: number
  LeagueId: number
  LeagueName: string
  LeagueIcon: number
  LeagueFrameIcon: number
  ResourceSpeed: number
  ResourceTotal: number

-- === league_pvp_tips ===
  SvrId: number
  LeagueId: number
  LeagueName: string
  LeagueIcon: number
  LeagueFrameIcon: number
  PvpScore: number

-- === mail_info ===
  iMailId: number
  arrAttachList: {  [repeated]
    iType: byte
    iId: number
    iAmount: number
    cExtraInfo: string
  }

-- === mail_simple_info ===
  iMailId: number
  cSenderName: string
  iSendTime: number
  iTextId: number
  iReadStatus: byte
  arrTitleParams: string [repeated]
  arrContentParams: string [repeated]
  iAttachStatus: byte
  iTimeOut: number

-- === normal_item_info ===
  ItemId: number
  Amount: number

-- === npair_number ===
  key: number
  value: number

-- === offlinepvp_hero_pos ===
  Pos: byte
  HeroCId: number

-- === offlinepvp_rival ===
  Uid: number
  RankId: number
  Fight: number

-- === peak_battle_data ===
  Uid: number
  Name: string
  FaceIcon: number
  FaceFrame: number
  Fight: number
  Level: number
  HostId: number
  Support: number

-- === peak_battle_log ===
  HostId: number
  Uid: number
  Name: string
  AvatarId: number
  AvatarFrameId: number
  Fight: number

-- === peak_member_data ===
  Index: byte
  MemberInfo: peak_battle_data

-- === peak_prize_record ===
  History: {  [repeated]
    Session: number
    Rank: number
  }

-- === peak_rank_data ===
  Uid: number
  Name: string
  FaceIcon: number
  FaceFrame: number
  HostId: number
  Level: number
  Fighting: number
  PickList: number [repeated]
  PeakRecords: peak_prize_record

-- === pvp_report ===
  PlayerTypeId: number
  PlayerName: string
  Avatar: number
  AvatarFrame: number
  MercenaryId: number
  HighestCombo: number
  HeroCId: number [repeated]
  TotalDamage: number [repeated]
  Integral: number

-- === rabbet_info ===
  Index: number
  Uid: number
  Status: byte

-- === replyinfo ===
  ReplyIdx: number
  ReplyUid: number
  ReplyInfo: {
    Uid: number
    Name: string
    AvatarId: number
    AvatarFrameId: number
  }
  RContent: string
  SendTime: number

-- === robot_info ===
  RobotId: number
  HeroId: number
  Fighting: number
  Level: number
  Name: string
  AvatarId: number
  AvatarFrameId: number

-- === rune_attr_info ===
  Uid: number
  Base: {  [repeated]
    Id: number
  }
  High: {  [repeated]
    Id: number
    Lv: number
  }

-- === rune_rabbet_info ===
  Id: number
  RabbetList: rabbet_info [repeated]

-- === season_info ===
  FightCount: number
  TotalFightCount: number
  WinCount: number
  TotalWinCount: number
  Wincombo: number
  TotalWincombo: number
  RunCount: number
  TotalRunCount: number

-- === secret_area_hero ===
  ClassId: number
  Strength: number
  ReturnTime: number

-- === secret_area_history ===
  Time: number
  StageGroupId: number
  StageLevel: number
  StageHierarchy: number
  RewardList: {  [repeated]
    ItemId: number
    Amount: number
  }

-- === secret_area_player ===
  UserUid: number
  HeroId: number
  Fighting: number
  Lv: number
  EquipRune: {  [repeated]
    Status: number
    Id: number
    Lv: number
  }

-- === secret_area_record ===
  WasteTime: number
  KeyId: number
  LevelRangeId: number
  StageId: number
  StageLevel: number
  TeamMembers: {  [repeated]
    Uid: number
    AvatarId: number
    AvatarFrameId: number
    HeroId: number
    Level: number
    Name: string
  }

-- === skill_level_info ===
  HeroUid: number
  SkillLevelInfo: {  [repeated]
    SkillId: number
    SkillLevel: number
  }

-- === spec_level_info ===
  HeroUid: number
  SpecLevelInfo: {  [repeated]
    SpecId: number
    SpecLevel: number
  }

-- === special_item_extra_attr ===
  RuneExtraAttr: rune_attr_info [repeated]
  EquipExtraAttr: equip_attr_info [repeated]
  ACardExtraAttr: attached_card_reform_info [repeated]

-- === special_item_info ===
  ItemId: number
  Uid: number
  Birthday: number
  ItemParamList: item_param
  ExtraAttr: special_item_extra_attr

-- === stage_drop_list_reward ===
  idx: number
  ItemId: number
  Count: number

-- === stage_reward ===
  ItemId: number
  count: number
  extra: string [repeated]

-- === taskinfo ===
  Id: number
  Type: number
  Status: number
  LoopTimes: number
  Cond: {  [repeated]
    Id: number
    CompCount: number
    ParamList: number [repeated]
  }

-- === team_apply_info ===
  Uid: number
  Name: string
  Lv: number
  TopLv: number
  MId: number
  Fighting: number
  SeverName: string
  Heros: {  [repeated]
    HeroId: number
    Fighting: number
  }

-- === team_commend_info ===
  Uid: number
  HostId: number
  Name: string
  Lv: number
  TopLv: number
  MId: number
  Heros: {  [repeated]
    HeroId: number
    Fighting: number
  }
  Extra: number [repeated]

-- === team_info ===
  Uid: number
  Leader: number
  Lv: number
  TotalScore: number
  Message: string
  SearcLv: byte
  Applys: team_apply_info [repeated]
  Members: team_member_info [repeated]
  PlayId: byte
  AutoAcc: byte
  Matching: byte
  Extra: {  [repeated]
    Key: byte
    Val: number
  }
  Robots: {  [repeated]
    Robot: robot_info
    Index: byte
  }

-- === team_invite_info ===
  Uid: number
  Name: string
  LeaderUid: number
  Lv: number
  TopLv: number
  MId: number
  Fighting: number
  AvatarId: number
  AvatarFrameId: number
  PlayId: number
  ServerName: string
  ExtraInfo: {  [repeated]
    Key: string
    Value: number
  }

-- === team_member_info ===
  Uid: number
  Name: string
  Index: byte
  Lv: number
  TopLv: number
  MId: number
  MLv: number
  RecentHeroList: {  [repeated]
    HeroId: number
    Lv: number
  }
  AvatarId: byte
  AvatarFrameId: byte
  ShapeId: number
  IsReady: byte
  OffTime: number
  Fighting: number
  Vitality: number
  ServerName: number
  LeagueUid: number
  VoiceId: number
  Title: number
  Extra: number [repeated]

-- === team_search_info ===
  Uid: number
  Leader: number
  Lv: number
  TotalScore: number
  Message: string
  SearcLv: byte
  Extra: {  [repeated]
    Key: byte
    Val: number
  }
  Members: {  [repeated]
    Uid: number
    Name: string
    Lv: number
    TopLv: number
    MId: number
    AvatarId: byte
    AvatarFrameId: byte
    LeagueUid: number
  }
  Robot: robot_info [repeated]

-- === top_rank_data ===
  Rank: number
  Number: number [repeated]
  String: string [repeated]

-- === user ===
  Uid: number
  Name: string
  Level: number
  TopLevel: number
  Gold: number
  BindGold: number
  HeroId: number
  CardUid: number
  Fighting: number
  ReNameTimes: number
  FirstRename: number
  TotalLoginDays: number
  PayZoneId: number
  CreateTime: number
  ShowHeroId: number

-- === userinfo ===
  Uid: number
  HideBirthday: byte
  SetBirthdayTime: number
  Year: number
  Month: byte
  Day: byte
  HideLocation: byte
  Location: string
  Sex: byte
  HideSex: byte
  AchieveNum: number
  SeasonPoint: number
  Badge: number [repeated]
  Tag: number [repeated]
  Heros: number [repeated]

-- === userinfo_other ===
  Uid: number
  Name: string
  Level: byte
  TopLevel: byte
  TotalScore: number
  AvatarId: byte
  AvatarFrameId: byte
  TitleId: number
  LeagueName: string
  AchieveNum: number
  Year: number
  Month: byte
  Day: byte
  Location: string
  Tag: number [repeated]
  Sign: string
  Dynamic: {  [repeated]
    Type: byte
    Param: number [repeated]
  }
  Sex: byte
  Badge: byte [repeated]
  Heros: {  [repeated]
    Cid: number
    Quality: byte
    Level: number
  }
  SeasonPoint: number
  ShowHeroId: number

-- === s_login_version ===
  ClientVersion: string
  PtoVersion: number
  VerifyStr: string

-- === s_login_reconnect ===
  ClientVersion: string
  PtoVersion: number
  VerifyStr: string
  CheckStr: string
  Urs: string
  Uid: number

-- === c_login_version ===
  server_id: number

-- === c_login_error ===
  errno: number
  strerror: string [repeated]

-- === c_data_begin ===
  Type: number
  Len: number
  FragmentAmount: number

-- === c_data_fragment ===
  FI: number
  DataFragment: string

-- === c_data_end ===
  Checksum: string

-- === c_chunk ===
  str: string

-- === s_new_udp_connect ===
  Uid: number
  GsId: number
  Client: string
  PtoCheck: number
  VerStr: string
  VerifyStr: string

-- === c_new_udp_connect ===
  Result: number
  MsgId: number
  MsgStr: string

-- === c_udp_connect_error ===
  errno: number
  strerror: string [repeated]

-- === c_peak_battle_task_info ===
  TaskList: {  [repeated]
    TaskType: number
    Count: number
  }
  TaskIdList: number [repeated]

-- === s_sendprize_exchange_count ===

-- === s_league_tech_shop_manager ===
  LeagueId: number
  HeroClass: number

-- === c_crosspvp_point ===
  AtkCount: dword
  OldPoint: number
  NewPoint: number
  OldRank: number
  NewRank: number
  OldRankId: number
  NewRankId: number

-- === s_peak_battle_group_info ===

-- === s_stage_activity_info ===

-- === c_battlefield_task_update ===
  task: battlefield_task

-- === s_campaign_fight ===
  StageId: number
  HeroUid: number
  Field: number
  AreaId: number

-- === s_scene_sync_pos ===
  X: number
  Y: number
  Z: number
  Face: number

-- === c_training_hero_info ===
  TrainingData: {
    HeroId: number
    ShapeId: number
    FashionId: number
    CardUid: number
    infos: {  [repeated]
      key: byte
      value: number
    }
    ChooseHero: {  [repeated]
      Mid: number
      HeroId: number
      PeakAttrId: number
      Attach: {  [repeated]
        key: number
        value: number
      }
    }
    CardSkillLevel: {  [repeated]
      HeroUid: number
      SkillLevel: {  [repeated]
        SkillId: number
        SkillLevel: number
      }
    }
    CardSpecLevel: {  [repeated]
      HeroUid: number
      SpecLevel: {  [repeated]
        SpecId: number
        SpecLevel: number
      }
    }
    RuneSpecList: {  [repeated]
      HeroUid: number
      SpecLevel: {  [repeated]
        SpecId: number
        SpecLevel: number
      }
    }
    Buffs: {  [repeated]
      HeroUid: number
      Id: number [repeated]
    }
    EquipHideAttr: {  [repeated]
      Id: number
      Value: number
    }
    AttachedCardBuff: {  [repeated]
      Id: number
      Lv: number
      Uid: number
    }
    ActiveCards: {  [repeated]
      ItemId: number
      Quality: number
      EnhanceLv: number
    }
    SupportSkill: {  [repeated]
      Index: byte
      HeroId: word
      ShapeId: number
      FashionId: number
    }
  }

-- === c_theater_unlock ===
  StageId: number
  Status: number

-- === s_team_recruit ===
  Msg: string
  Channels: number [repeated]

-- === s_time_ping_up ===
  DiffTime: number

-- === s_achieve_open ===
  Type: number

-- === c_stage_choose_loading ===
  StageId: number
  Extra: {  [repeated]
    Key: string
    Value: number
  }
  MerberLoadInfo: {  [repeated]
    Uid: number
    Name: string
    Index: byte
    Lv: number
    TopLv: number
    AvatarId: byte
    AvatarFrameId: byte
    IsLeader: byte
  }
  IsBack: byte

-- === c_act_hero_bp_active ===
  ActId: number
  ItemList: {  [repeated]
    Id: number
    Count: number
  }

-- === c_server_frame_local ===
  DataIndex: number

-- === c_card_support_skill ===
  Supports: {  [repeated]
    HeroCId: number
    Index: number
    SupportHeroCId: number
    IsAuto: byte
  }

-- === c_zhanling_info ===
  ActId: number
  TaskList: {  [repeated]
    Id: number
    Status: byte
    Val: number
    VipReward: byte
  }
  zhanling: byte [repeated]

-- === c_pressure_task_reward ===
  TaskType: byte
  TaskId: number

-- === s_team_commend ===
  PlayId: number
  CommendType: number

-- === c_chaos_match_cancel ===

-- === s_friend_quick_send_strength ===

-- === s_danmu_change_icon ===
  Icon: number

-- === c_peak_battle_primary_change_hero ===
  HeroCId: number

-- === c_stage_activity_info ===
  ProgressInfo: {  [repeated]
    Id: number
    State: number
  }

-- === s_guide_finish ===
  setIdList: number [repeated]
  guideIdList: number [repeated]

-- === c_peak_battle_ban_hero ===
  MyIsBan: byte
  MyBanList: number [repeated]
  RivalIsBan: byte
  RivalList: number [repeated]

-- === c_crosspvp_match ===
  TargetInfo: {
    Name: string
    Level: number
    TopLevel: number
    FaceIcon: dword
    FaceFrame: dword
  }

-- === c_frame_new_correct_do ===
  Frame: number

-- === c_stage_crosspvp_pos ===
  AtkPos: crosspvp_pos [repeated]
  DefPos: crosspvp_pos [repeated]
  AtkInfo: {
    Name: string
    Fighting: number
    Level: word
    RankId: word
    Point: word
    HostId: dword
  }
  DefInfo: {
    Name: string
    Fighting: number
    Level: word
    RankId: word
    Point: word
    RobotId: number
    HostId: dword
  }

-- === c_home_furniture_produce_update_list ===
  Data: furniture_produce [repeated]

-- === c_act_team_info ===
  TeamList: {  [repeated]
    Uid: number
    Name: string
    Avatar: number
    AvatarFrame: number
    ShapeId: number
    Point: number
    CanKick: byte
  }

-- === s_scene_line_change ===
  SceneId: number
  LineId: number

-- === s_attached_lot_compose ===
  Star: number
  Cost: number
  ComposeNum: number

-- === s_battlefield_pk_cancel_invite ===

-- === c_league_invite_del ===
  SourceUid: number

-- === c_herochip_stage_finish ===
  RewardList: stage_reward [repeated]
  LeagueItems: stage_reward [repeated]

-- === s_pay_check ===
  ShopId: number
  GoodsId: number
  Price: number
  Amount: number

-- === c_entrust_task_del ===
  TaskUniqId: number

-- === c_interaction_use_mood ===
  MoodId: number
  Result: byte

-- === c_userinfo_badge ===
  List: {  [repeated]
    Id: byte
    Value: number
    State: byte
    Time: number
  }

-- === s_equip_dieset_enhance ===
  EquipPos: byte
  DiesetIndex: byte
  DiesetLv: byte
  DiesetProgress: dword

-- === c_act_exercise_info ===
  ActId: number
  StageList: {  [repeated]
    Id: number
    State: byte
    StartTime: number
    RewardList: {  [repeated]
      ItemId: number
      Count: number
      IsSuper: byte
    }
    HeroList: {  [repeated]
      Index: number
      HeroCId: number
    }
  }

-- === c_chat_frame_info ===
  Using: number
  Info: {  [repeated]
    Id: number
    Value: number
    State: byte
  }

-- === c_attached_card_reform ===
  ACardUids: number
  Index: number
  Val: number

-- === c_campaign_task_finish ===
  Id: number
  Reward: stage_reward [repeated]

-- === s_business_extend_info ===

-- === c_peak_battle_primary_ready_fight ===
  Time: number

-- === c_userinfo_location_set ===
  HideLocation: byte
  Location: string

-- === s_frame_obj_report_local ===
  DataIndex: number
  ReportList: {  [repeated]
    Uid: number
    CFrame: number
    AtrType: byte
    Data: {  [repeated]
      id: number
      value: number
      extval: number
      extdata: number [repeated]
    }
  }

-- === c_league_up_level ===
  LeagueId: number
  Lv: byte
  Exp: number
  Money: number

-- === s_league_pvp_result ===

-- === c_group_team_invite ===
  GroupId: number
  TargetUid: number

-- === s_interaction_config_exchange ===
  Type: byte
  SrcIndex: number
  DstIndex: number
  HeroId: number

-- === s_peak_battle_primary_ready_fight ===
  IsAgree: number

-- === c_act_exchange_update ===
  ActId: number
  Id: number
  Times: number
  Unlock: byte
  UnlockNum: number

-- === c_act_return_update ===
  BounsList: {  [repeated]
    Id: number
    Count: number
  }
  GoodsList: {  [repeated]
    Id: number
    Count: number
  }

-- === s_new_hero_fight ===
  StageId: number
  ActId: number

-- === s_league_audit_panel ===
  LeagueId: number

-- === c_home_furniture_produce_list ===
  Data: furniture_produce [repeated]

-- === s_danmu_update ===
  Type: number
  ID: number
  Msg: string
  Postion: byte
  Color: byte

-- === c_card_resonance_lvup ===
  Uid: number
  ResonnanceLv: number
  OldHeroId: number
  NewHeroId: number

-- === s_league_up_level ===
  LeagueId: number

-- === s_entrust_task_list ===
  Version: number

-- === c_battlefield_pk_ready ===
  Uid: number
  Name: string
  Rank: number
  ShapeId: number
  MercenaryList: number [repeated]

-- === c_attached_card_active_book ===
  ItemId: number
  Type: number

-- === s_group_enter_area ===
  AreaId: number

-- === s_group_team_choose_list ===
  GroupId: number

-- === s_toplist_pages ===
  ID: byte
  SubName: number
  PageNums: number [repeated]
  SelfUid: number
  IsCross: number

-- === c_reddot_update ===
  RedDot: {  [repeated]
    Id: number
    RedNum: number
  }

-- === c_group_team_apply_clear ===
  GroupId: number

-- === c_top_level_update ===
  Id: number
  State: byte

-- === s_server_frame_local ===
  DataIndex: number
  FrameList: {  [repeated]
    FrameId: number
    FrameData: {  [repeated]
      Cmd: number [repeated]
    }
  }

-- === s_friend_quick_recive_strength ===

-- === s_offlinepvp_info ===

-- === s_city_level_click ===
  Level: word

-- === c_fashion_info ===
  List: {  [repeated]
    Id: number
    State: byte
    EndTime: number
  }

-- === s_equip_lock ===
  EquipUid: number

-- === c_battlefield_task_finish ===
  Index: byte
  TaskId: number

-- === c_chaos_protect_score ===
  AddScore: number

-- === s_league_tech_pre_buy ===
  LeagueId: number
  WeekTechId: number
  Result: byte

-- === c_toplist_first ===
  List: {  [repeated]
    ID: byte
    SubName: number
    RankInfo: {
      Number: number [repeated]
      String: string [repeated]
    }
    IsCross: number
  }

-- === s_platform_access_friend_share_panel ===

-- === s_scene_leave_seamless ===
  X: number
  Y: number
  Z: number

-- === s_stage_finish_loading ===

-- === c_group_result ===
  Result: number
  ConsumeTime: number
  UidsRewards: {  [repeated]
    Uid: number
    Rewards: stage_reward [repeated]
  }

-- === c_rogue_endless_phase ===
  phase: number
  score: number

-- === s_theater_bonus ===
  CfgType: number
  BonusIdx: number

-- === s_league_rank_week_no ===

-- === s_area_event_hero_list ===
  Type: number
  Lineup: number [repeated]

-- === s_act_daily_stage_enter ===
  ActId: number
  Id: number
  HeroId: number
  IsPeakAttr: byte

-- === s_home_role_mood_list ===

-- === s_team_action ===
  IsAcc: number

-- === c_team_auto_acc ===
  AutoAss: number

-- === c_league_sync_attr_int ===
  LeagueId: number
  SyncAttr: {  [repeated]
    key: byte
    value: number
  }

-- === c_act_goods_buy ===
  ActId: number
  GoodsId: number

-- === s_battlefield_task_reward ===
  RewardType: byte

-- === s_training_finish ===
  HeroCId: number
  SkillId: number

-- === s_league_tech_buy ===
  LeagueId: number
  BuyType: byte
  Id: number

-- === s_avatar_use ===
  Id: number

-- === c_userinfo_sex_set ===
  Sex: byte
  HideSex: byte

-- === c_battlefield_pk_invite ===

-- === s_theater_unlock ===
  StageId: number

-- === s_skill_spec_reset ===
  HeroUid: number

-- === c_league_pvp_view_member_records ===
  IsRival: number
  LeaguePvpMemberRecords: league_pvp_member_record [repeated]

-- === s_equip_off ===
  EquipPos: number

-- === c_league_tech_progress_reward ===
  LeagueId: number
  WeekTechId: number
  RewardId: number [repeated]

-- === s_act_magic_shop_draw ===

-- === c_scene_interaction_change ===
  Type: byte
  Uid: number
  EmoticonId: number

-- === s_equip_remould ===
  EquipPos: byte
  RemouldLv: byte
  RemouldProgress: dword

-- === s_log_push_gift ===
  PushList: {  [repeated]
    Id: number
    Type: byte
    Name: string
  }

-- === c_league_boss_panel ===
  LeagueRealDayNo: word
  StartTime: dword
  Damage: number
  UserRealDayNo: word
  RecordLeagueId: number
  ChallengeTimes: byte
  AddChallengeTimes: byte
  RewardList: number [repeated]

-- === c_stage_finish_times ===
  StageId: number
  Times: number

-- === s_league_modify_ad ===
  LeagueId: number
  Ad: string

-- === c_league_pvp_stage_data ===
  StageDataList: {  [repeated]
    Uid: number
    HeroCId: number
    Camp: number
    Hp: number
  }
  MaxLv: number

-- === c_comment_reply_list ===
  SIdx: number
  EIdx: number
  List: replyinfo [repeated]

-- === s_office_pick_daily ===
  Index: number

-- === c_group_stage_status ===
  AreaId: number
  Index: number
  Status: number
  TeamList: number [repeated]
  RepairTime: number

-- === s_friend_accept ===
  Uid: number

-- === s_comment_reply ===
  Mod: string
  ModId: number
  SendUid: number
  ModIdIdx: number
  Content: string

-- === s_league_pvp_view_panel ===

-- === s_act_mini_game_report ===
  ActId: number
  Id: number
  BoxList: {  [repeated]
    Id: number
    Count: number
  }
  Param: number [repeated]

-- === c_crosspvp_buy ===
  Times: word

-- === c_theater_open ===
  ChapterInfo: {  [repeated]
    Id: number
    Status: number
    BonusInfo: {  [repeated]
      Star: number
      BonusTime: number
    }
  }
  StageInfo: {  [repeated]
    Id: number
    Status: number
    StarList: number [repeated]
    FullStarTime: number
    DramaFinish: number [repeated]
    ViewTimes: number
  }
  BonusInfo: {  [repeated]
    Idx: number
    BonusTime: number
  }
  GlobalBonusInfo: {  [repeated]
    Idx: number
    BonusTime: number
  }
  UserContri: number
  GlobalContri: number

-- === c_equip_enhance ===
  EquipPos: byte
  EnhanceRes: byte
  EnhanceLv: number
  FailCount: number

-- === s_send_pvp_report_data ===
  UserUid: number
  HighestCombo: number
  HeroCId: number [repeated]
  TotalDamage: number [repeated]

-- === s_friend_delblack ===
  Uid: number

-- === c_hero_rank_star_reward_update ===
  Id: number
  State: byte

-- === c_rogue_pass_info ===
  IsStart: number
  Difficult: number
  MaxDifficult: number [repeated]
  GroupId: number
  HeroIndex: number
  PassBuffList: number [repeated]
  StageBuffList: number [repeated]
  FinishStageList: {  [repeated]
    Id: number
    Score: number
  }
  MaxHp: number
  CurHp: number
  ChooseBuff: number [repeated]
  ChooseBuff2: number [repeated]
  InnerCoin: number
  IsInHide: number
  ShopInfo: {
    BuffList: number [repeated]
    HadBuyList: number [repeated]
    Discount: number
    FreeIndex: number
  }
  BossStageId: number
  HpItemTimes: number
  HideRewardTimes: number
  AttachCard: number [repeated]

-- === c_team_change_hero ===
  UserUId: number
  HeroId: number
  Fighting: number
  Vitality: number
  ShapeId: number
  MLv: number

-- === c_battlefield_task_reward ===
  RewardType: byte

-- === c_act_hero_task_update ===
  ActId: number
  TaskList: {  [repeated]
    Id: number
    Value: number
    State: byte
    ExtValue: number
    ExtState: byte
  }

-- === c_skill_get_skill_level ===
  SkillInfo: skill_level_info

-- === s_battlefield_solo_info ===

-- === s_battlefield_pk_handle ===
  Uid: number
  Accpet: byte
  MsgId: number

-- === c_master_shop_buy ===
  ShopId: number
  GoodsId: number
  RemainAmount: number
  HadAmount: number

-- === s_stage_damage_info ===
  Members: {  [repeated]
    UserUid: number
    HurtSum: number
  }
  MaxCombo: number
  MvpUserUid: number
  Reborn: number

-- === c_secret_insert_key ===
  KeyOwerUid: number
  KeyId: number

-- === c_team_acc_invite ===
  TeamUid: number

-- === c_rogue_pass_exit ===

-- === c_team_deal_apply ===
  TargetUid: number

-- === c_league_tech_shop_manager ===
  LeagueId: number
  ManagerUid: number
  ManagerName: string
  HeroClass: number
  JoinTime: dword

-- === c_puzzle_update ===
  Id: byte
  Value: number
  State: byte

-- === s_lantern_hit ===
  Row: byte
  Col: byte

-- === s_async_cfg_check ===
  CheckList: {  [repeated]
    AsyncId: byte
    Key: number
    Version: number
  }
  langtype: string

-- === s_training_enter ===
  HeroCId: number
  StageId: number

-- === s_top_level_info ===

-- === c_achieve_overview ===
  TypeList: {  [repeated]
    PageId: number
    CurNum: number
    Point: number
    RedDot: byte
  }
  FinishList: {  [repeated]
    Id: number
    GetTime: number
  }

-- === c_usj_update_score ===
  ServerTotalScore: number
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === c_night_fight_floor_reward ===
  StageId: number

-- === c_offlinepvp_pro_reward ===
  CulCount: number
  CulTime: number
  CulSumTime: number
  RewardList: stage_reward [repeated]

-- === s_act_eye_sight_report ===
  Record: number

-- === s_ping_fight_list ===
  PingValue: number [repeated]

-- === s_battlefield_pk_quit ===

-- === s_battlefield_solo_reward ===
  Id: number

-- === s_puzzle_reward ===

-- === s_admission_manual_sync_info ===

-- === c_interaction_data ===
  EmojiLibData: number [repeated]
  AnimLibData: number [repeated]
  MoodLibData: number [repeated]
  EmojiCfgData: {  [repeated]
    Index: number
    Id: number
  }
  AnimCfgData: {  [repeated]
    Index: number
    Id: number
  }
  MoodCfgData: {  [repeated]
    Index: number
    Id: number
  }
  CurMood: number

-- === c_league_icon ===
  LeagueId: number
  HeadIcon: number [repeated]
  HeadFrameIcon: number [repeated]

-- === s_peak_battle_honor_info ===
  Season: number
  IsCross: byte

-- === s_office_pick_weekly ===
  Index: number

-- === c_team_offline ===
  Uid: number
  offTime: number

-- === c_battlefield_solo_update ===
  AchieveList: {  [repeated]
    Id: number
    Value: number
    State: byte
  }

-- === s_userinfo_info ===

-- === c_base_station_activate ===
  iBaseStationId: byte
  iResult: byte

-- === c_act_pickbox_update ===
  ActId: number
  PoolId: number
  FreeCount: byte
  GetList: {  [repeated]
    Id: number
    GetNum: number
  }
  RewardList: {  [repeated]
    AddLog: stage_reward [repeated]
    IsImportant: byte
  }

-- === s_peak_battle_primary_change_hero ===
  HeroCId: number

-- === c_peak_battle_primary_info ===
  SeatList: {  [repeated]
    SeatStatus: number
    Time: number
    FaceIcon: number
    FaceFrame: number
  }
  SeatId: number
  ChallengeCD: number
  ChallengeCount: number
  ShopCount: number
  HeroCId: number

-- === s_group_channel_load ===
  GroupId: number
  ChannelId: number

-- === c_admission_manual_sync_info ===
  CondData: {  [repeated]
    Id: word
    Count: number
    Status: byte
  }

-- === c_league_ad_panel ===
  LeagueId: number
  AdTimes: byte

-- === s_campaign_buy ===
  ShopId: number
  Pos: byte
  Count: number
  CurCount: number

-- === s_pay_info ===
  shopid: number [repeated]

-- === c_chat_public ===
  ChatList: {  [repeated]
    ChannelId: byte
    Msg: string
    SenderInfo: {
      Uid: number
      Name: string
      Level: byte
      TopLevel: number
      AvatarId: byte
      AvatarFrameId: byte
      ChatFrameId: byte
      HostId: number
    }
    Links: string
    ExtData: string
  }

-- === s_league_board_comment_oper ===
  LeagueId: number
  BoardId: number
  CommentId: number
  OpType: number
  Msg: string

-- === s_group_open_map ===

-- === c_league_change_name ===
  LeagueId: number
  Name: string
  ChangeNameCardAmount: number

-- === s_act_empty_shop_stage_reenter ===
  StageIndex: number
  HeroUid: number

-- === s_flipcard_total_reward ===

-- === s_training_info ===

-- === c_egg_task_add ===
  ETasks: egginfo [repeated]

-- === s_relax_cond_get_reward ===
  Type: byte
  Id: number

-- === s_secret_apply_insert_key ===
  KeyId: number

-- === c_week_sign_info ===
  Type: byte
  ActId: number
  Week: byte
  WeekList: {  [repeated]
    DayList: {  [repeated]
      Day: byte
      State: byte
    }
  }

-- === s_offlinepvp_note ===

-- === s_sendprize_exchange ===
  ExchangeIndex: number
  ExchangeCount: number

-- === s_pressure_like_info ===

-- === c_secret_area_history ===
  HistoryList: secret_area_history [repeated]

-- === c_peak_battle_honor_info ===
  Season: number
  IsCross: byte
  RankList: peak_rank_data [repeated]
  MyPeakRecords: peak_prize_record

-- === s_stage_achievement_finish ===
  IdList: number [repeated]

-- === c_act_client_trigger_info ===
  ActId: number
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === c_scene_player_create ===
  List: {  [repeated]
    Uid: number
    X: number
    Y: number
    Z: number
    ShapeCacheId: number
    Climbing: climbing
    Version: number
  }

-- === c_area_event_fight_over ===
  StageId: number
  IsWin: number
  Star: byte

-- === c_all_server_cond_get_info ===
  ServerCondInfo: {  [repeated]
    Id: number
    Status: byte
    PlayerList: {  [repeated]
      Uid: number
      Name: string
      AvatarId: byte
      AvatarFrameId: byte
      Time: number
    }
  }

-- === c_user_update ===
  user: user

-- === s_group_team_create ===
  GroupStageId: number
  ShowStatus: byte
  GroupDesc: string
  Difficult: number
  FightLimit: number

-- === s_gem_resolve ===
  HeroCId: number
  SkillId: number
  Pos: number

-- === c_peak_battle_primary_seat_info ===
  SeatIndex: number
  SeatData: {  [repeated]
    SeatStatus: number
    UserName: string
    ConWinCount: number
  }

-- === s_campaign_leave ===

-- === s_act_boss_challenge_svr_point ===

-- === s_resident_enter ===
  TypeId: number
  Rank: number

-- === s_campaign_control_update ===
  ControlUid: number

-- === c_time_ping ===
  SendTime: number
  ServerTime: number

-- === c_collect_info ===
  Sys: {  [repeated]
    Type: byte
    List: {  [repeated]
      Id: number
      Value: number
      State: byte
    }
  }

-- === s_peak_battle_primary_shop_count ===
  Count: number

-- === c_growth_fund_info ===
  IsActive: number [repeated]
  Data: {  [repeated]
    Id: number
    Status: number
  }

-- === c_business_extend_report ===
  shopTime: number
  businessId: number
  supportList: number [repeated]
  finishCount: number
  supportReward: number
  rewards: {  [repeated]
    itemId: number
    count: number
  }

-- === c_chaos_info ===
  Period: number
  Score: number
  BanHeroCId: number [repeated]
  HadBanHero: number [repeated]
  CurBanHero: number [repeated]
  Info: {  [repeated]
    HeroClassId: number
    Count: number
    Time: number
  }
  PenaltyTime: number [repeated]

-- === s_scene_shape_cachedata ===
  ShapeCacheId: number

-- === c_act_winding_sync_info ===
  DailyStatus: number
  DayTimes: number
  TotalTimes: number
  Points: number [repeated]
  RewardStatus: {  [repeated]
    id: number
    status: number
  }
  TotalDay: number

-- === c_group_play_sync ===
  Infos: {  [repeated]
    Uid: number
    LoadValue: number
    Disconnect: number
  }

-- === s_world_task_pick_prestige ===

-- === s_group_quit ===

-- === c_activity_shop_info ===
  BuyInfo: {  [repeated]
    GoodsId: number
    BuyTimes: number
  }

-- === c_relax_stage_finish ===
  Players: {  [repeated]
    Uid: number
    TrueItem: {  [repeated]
      ItemId: number
      Num: number
    }
    FakeItem: {  [repeated]
      ItemId: number
      Num: number
    }
    LeagueItems: stage_reward [repeated]
    Dps: number
    MaxCombo: number
    Reborn: number
    LeagueDraw: byte
  }
  MvpUserUid: number
  WasteTime: number

-- === c_team_ask_for_leader ===

-- === c_league_apply ===
  LeagueId: number
  Result: byte

-- === c_world_task_extra_reward ===
  TaskId: number
  Reward: stage_reward [repeated]

-- === c_business_extend_info ===
  businessId: number
  day: number
  supportList: number [repeated]
  showId: number
  taskList: {  [repeated]
    value: number
    isGet: number
  }

-- === c_league_board_public ===
  LeagueId: number
  LastPubTime: number
  CDTime: number

-- === c_pay_info ===
  GoodsInfo: {  [repeated]
    GoodsId: number
    ShopId: number
    GoodsName: string
    GoodsIcon: string
    GoodsBg: string
    Sequence: number
    BuyCond: string
    LimitTimes: number
    PriceType: string
    Price: number
    ProductId: string
    LeftTimes: number
    GiftBag: number
    BagAmount: number
    EndTime: number
    PageId: number
    ShowPriceType: string
    ShowPrice: number
    IsFirstPay: number
    ViewConf: string
    PreToken: {  [repeated]
      Token: string
      Time: number
    }
  }
  CurPage: number
  MaxPage: number

-- === s_crosspvp_top_list ===
  Season: number
  Page: number [repeated]

-- === s_peak_battle_group_ready ===

-- === s_login_drama ===
  StageId: number

-- === s_team_back_room ===

-- === c_scene_line_info ===
  SceneId: number
  Line: number
  List: {  [repeated]
    LineId: number
    SceneId: number
    Status: number
  }

-- === c_act_mini_game_enter ===
  ActId: number
  Id: number

-- === s_stage_time_pause ===
  Status: byte

-- === c_secret_apply_insert_key ===
  KeyOwerUid: number
  KeyId: number
  OwnerName: string

-- === c_item_update_use_count ===
  ItemId: number
  DayUseCount: byte
  WeekUseCount: byte

-- === s_friend_send_msg ===
  Uid: number
  Msg: string
  ItemLinks: string

-- === s_friend_addblack ===
  Uid: number

-- === c_user_sync_int ===
  AttrList: {  [repeated]
    Key: number
    Value: number
  }

-- === c_frame_new_correct ===

-- === c_grid_box_reset ===
  ActId: number
  times: number

-- === c_group_channel_list ===
  GroupId: number
  ChannelList: {  [repeated]
    ChannelId: number
    Load: number
    No: number
  }
  Page: word
  ChannelAmount: number

-- === c_all_server_cond_list ===
  IdList: number [repeated]
  IsEnd: number

-- === c_group_obj_info ===
  Time: number
  GroupObjsData: {  [repeated]
    Id: number
    DayCount: number
    WeekCount: number
  }
  HerosData: {  [repeated]
    HeroId: number
    Count: number
  }

-- === c_hero_rank_info ===
  TotalStar: number
  HeroStar: {  [repeated]
    Cid: number
    Star: number
  }
  TaskList: {  [repeated]
    Id: number
    Value: number
    State: byte
  }
  LastStarId: number
  LastStarState: byte
  BuffList: number [repeated]

-- === c_city_level_click ===
  Level: word

-- === c_act_ach_info ===
  ActId: number
  List: {  [repeated]
    Id: number
    Value: number
    State: byte
    Time: number
  }

-- === s_league_pvp_enter_scene ===

-- === c_team_clear_apply ===
  TargetUid: number

-- === c_secret_area_stage_finish ===
  Members: {  [repeated]
    UserUid: number
    DrawItems: item_data [repeated]
    FakeItems: item_data [repeated]
    ExtraItems: extra_item_data [repeated]
    LeagueItems: stage_reward [repeated]
    HurtSum: number
    MaxCombo: number
    Reborn: number
    LeagueDraw: byte
  }
  MvpUserUid: number
  ScoreLevel: number
  HierarchyUp: number
  WasteTime: number
  KeyId: number
  StageLevel: number

-- === c_act_allsvr_stage_info ===
  ActId: number
  AreaInfo: {
    Id: number
    Difficult: byte
    LevelList: {  [repeated]
      Id: number
    }
  }
  AllSvrScore: number
  AllSvrCond: {  [repeated]
    Id: number
    State: byte
  }
  BossInfo: {
    Id: number
    Count: number
    BestScore: number
    TodayScore: number
  }

-- === c_achieve_open ===
  Info: achieveinfo [repeated]

-- === s_league_money_log ===
  LeagueId: number
  LeagueMoneyLogNo: number

-- === c_home_owner_info ===
  Info: home_liker

-- === s_friend_getinfo ===
  Type: number

-- === s_resource_stage_info ===

-- === c_item_del ===
  ItemUid: number [repeated]

-- === c_teach_pvp ===
  GuideId: number

-- === s_league_invite ===
  TargetUid: number

-- === s_group_team_apply ===
  GroupId: number

-- === c_friend_sync_qinmi ===
  uid: number
  qinmi: number

-- === c_zhanling_active ===
  ActId: number
  Id: number

-- === c_avatar_unlock ===
  AvatarList: number [repeated]
  FrameList: number [repeated]

-- === c_relax_stage_sync_times ===
  DailyBoxTimes: number
  TotalBoxTimes: number
  DailyRewardTimes: number
  TotalRewardTimes: number

-- === c_chaos_choose_info ===
  Info: {  [repeated]
    Uid: number
    HeroClassId: number
    SelectType: number
  }

-- === c_campaign_buy ===
  ShopId: number
  Pos: byte
  Count: number

-- === c_theater_bonus ===
  CfgType: number
  BonusIdx: number
  Reward: {  [repeated]
    Id: number
    Amount: number
  }

-- === c_team_change_leader ===
  TargetUid: number

-- === s_login_account_enter ===
  Account: string
  Password: string

-- === s_peak_battle_primary_reset_cd ===

-- === s_item_sell ===
  SellType: byte
  NormalItemList: {  [repeated]
    ItemId: number
    Amount: number
    NowAmount: number
  }
  SpecialItemUidList: number [repeated]

-- === c_act_attr_update ===
  ActId: number
  IntAttrList: {  [repeated]
    Key: byte
    Value: number
  }
  StrAttrList: {  [repeated]
    Key: byte
    Value: string
  }

-- === s_flipcard_flip ===
  Idx1: number
  Idx2: number
  State: byte

-- === c_area_event_wipe ===
  AreaEventId: number

-- === c_skill_spec_reset ===
  SpecInfoList: spec_level_info

-- === s_group_team_change_leader ===
  GroupId: number
  TargetUid: number

-- === c_attached_card_sync_reform ===
  ReformList: attached_card_reform_info

-- === s_rogue_benefit_choose ===
  ChooseType: number
  BuffIndex: number

-- === s_act_get_reward ===
  ActId: number
  RewardId: number
  NumList: number [repeated]
  StrList: string [repeated]

-- === c_friend_find ===
  Info: friendinfo [repeated]

-- === c_comment_delcomment ===
  CommentId: number
  SenderUid: number
  CommentIdx: number

-- === c_act_rescue_top ===
  StageList: {  [repeated]
    Id: byte
    Point: number
    Name: string
    Avatar: number
    AvatarFrame: number
  }

-- === c_team_action ===
  UserUid: number
  IsAcc: number

-- === c_userinfo_tag ===
  List: {  [repeated]
    Id: byte
    State: byte
  }

-- === c_league_rank_week_no ===
  week_no: number

-- === s_friend_sync_int ===
  key: byte [repeated]

-- === c_league_tech_join ===
  LeagueId: number
  WeekTechId: number
  HeroClass: number
  JoinCount: byte
  Progress: number
  Time: number
  JoinNo: byte

-- === c_battlefield_pk_cancel_invite_ret ===

-- === s_comment_delcomment ===
  Mod: string
  ModId: number
  SenderUid: number
  ModIdIdx: number

-- === c_card_feed ===
  CardUid: number
  IsSuccess: number

-- === c_rune_oper ===
  Uid: number
  Type: number
  MId: number
  Index: byte

-- === c_income_buff_info ===
  List: {  [repeated]
    Id: number
    EndTime: number
  }

-- === c_scene_trigger_state ===
  Uid: number
  State: number

-- === s_league_pvp_quit ===

-- === s_peak_battle_bet_info ===

-- === s_base_station_activate ===
  iBaseStationId: byte

-- === c_stage_leave ===
  StageId: number

-- === s_collect_info ===

-- === c_offlinepvp_rank_up ===
  OldRankId: number
  NewRankId: number
  TopRankId: number
  IsPromoto: number
  Reward: stage_reward [repeated]

-- === s_card_take_bio_reward ===
  CardUid: number
  BiographyId: number

-- === s_comment_like ===
  Mod: string
  ModId: number
  SendUid: number
  ModIdIdx: number

-- === c_hero_rank_star_update ===
  Total: number
  Cid: number

-- === c_league_tech_modify_notic ===
  LeagueId: number
  TechNotic: string

-- === s_chaos_fight_record ===

-- === c_act_boss_challenge_svr_point ===
  TotalPoint: number

-- === s_pay_item_confirm ===
  ShopId: number
  GoodsId: number
  Token: string
  CheckType: number
  Reason: string

-- === c_act_winding_sub_toplist ===
  WindId: number
  UpdateTime: number
  TopList: {  [repeated]
    name: string
    avatarid: number
    avatarframeid: number
    score: number
    nums: number
    time: number
  }

-- === s_act_boss_challenge_svr_ach_reward ===
  AchId: number

-- === s_league_pvp_view_info ===
  IsRival: number

-- === c_act_allsvr_stage_update_boss ===
  ActId: number
  BossInfo: {
    Id: number
    Count: number
    Score: number
    BestScore: number
    TodayScore: number
  }

-- === c_league_tech_normal_event_info ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte
  EventProgress: byte
  EventStoryList: {  [repeated]
    StoryId: number
    StoryParams: string [repeated]
  }
  DealTimes: byte

-- === s_comment_list ===
  Mod: string
  ModId: number
  Page: number

-- === s_campaign_sync_pos ===
  UserPos: campaign_pos

-- === c_rune_lock ===
  Uid: number
  Type: number

-- === c_theater_finish ===
  newChapterInfo: {  [repeated]
    Id: number
    Status: number
  }
  newStageInfo: {  [repeated]
    Id: number
    Status: number
  }

-- === c_group_team_swap_pos ===
  GroupId: number
  Pos1: byte
  Pos2: byte

-- === s_softball_throw ===
  Power: number
  Angle: number

-- === s_offlinepvp_fight ===
  RankId: number

-- === s_friend_delfriend ===
  Uid: number

-- === c_danmu_get_total_amount ===
  iType: number
  iPlotId: number
  iTotalAmount: number

-- === c_lantern_info ===
  RowNum: byte
  ColNum: byte
  GqId: number
  Cell: number [repeated]
  PCount: number
  TbGet: number [repeated]

-- === s_peak_battle_get_task_reward ===
  TaskId: number

-- === s_act_return_check_goods ===
  Id: number
  Count: number

-- === c_gem_list ===
  Total: number
  HeroGemData: hero_gem_data [repeated]

-- === s_master_shop_buy ===
  ShopId: number
  GoodsId: number
  Amount: number
  CurrencyAmount: number

-- === c_equip_merge_to ===
  EquipUid: number

-- === c_campaign_hero_info_update ===
  Data: campaign_hero_info

-- === c_scene_player_delete ===
  List: number [repeated]

-- === s_grid_box_lottery ===
  ActId: number
  LotteryType: byte
  CouponCount: number

-- === c_pressure_stage_detail ===
  TotalScore: number
  TotalRank: number
  StageId: number
  StageScore: number
  StageRank: number
  TopList: {  [repeated]
    Rank: byte
    Number: number [repeated]
    String: string [repeated]
  }
  Count: byte
  HeroList: {  [repeated]
    HeroId: number
    Power: number
  }
  StageLevel: byte

-- === c_home_like ===
  Uid: number
  LikeOrCancel: byte

-- === s_friend_quick_deal_with_apply ===
  TargetUids: number [repeated]
  Result: byte

-- === s_exchange_code ===
  code: string

-- === c_usj_enter_stage ===
  ZoneId: number
  PointId: number
  HeroUid: number

-- === c_once_recharge_info ===
  Id: number
  RechargeCount: number
  GetCount: number

-- === c_chaos_season_info ===
  SeasonId: number
  RankWinCount: number
  RankLoseCount: number
  CommWinCount: number
  CommLoseCount: number

-- === c_usj_load ===
  ServerTotalScore: number
  UserTotalScore: number
  HeroList: {  [repeated]
    HeroUid: number
    HpPercent: number
    DeathTime: number
  }
  ZoneList: {  [repeated]
    ZoneId: number
    AccessedPath: number [repeated]
    ZoneRewards: {  [repeated]
      RewardType: byte
      RewardState: byte
    }
    PointRewards: {  [repeated]
      PointId: number
      RewardState: byte
    }
    ScoreList: {  [repeated]
      PointId: number
      Score: number
    }
  }
  OpenZone: {  [repeated]
    ZoneId: number
    Reason: byte
  }
  LevelRangeId: number
  CurrentZoneId: number
  CurrentPointId: number
  CurrentHeroUid: number
  RankReward: number
  HaveShowEndReward: byte
  IsFirstTime: byte
  ThemeId: number
  NextThemeId: number
  ScoreReward: {  [repeated]
    Id: number
    State: byte
  }

-- === c_league_search ===
  LeagueInfo: {  [repeated]
    LeagueId: number
    LeagueName: string
    HeadIcon: number
    HeadFrameIcon: number
    Lv: byte
    MemberAmount: word
    WeekGongXun: number
    Ad: string
    LeaderUid: number
    LeaderName: string
  }

-- === c_hero_rank_stage_info ===
  StageList: {  [repeated]
    Id: number
    Star: byte [repeated]
  }

-- === c_act_ach_update ===
  ActId: number
  List: {  [repeated]
    Id: number
    Value: number
    State: byte
    Time: number
  }

-- === s_mail_delete ===
  arrMailIds: number [repeated]

-- === c_lantern_hit ===
  Row: byte
  Col: byte
  IsWin: byte
  Reward: stage_reward [repeated]

-- === s_act_user_info ===
  ActId: number

-- === c_userinfo_hero_set ===
  Heros: number [repeated]

-- === c_team_attr ===
  AttrName: string [repeated]
  Value: number [repeated]
  AttrNameStr: string [repeated]
  ValueStr: string [repeated]
  ExtraKey: string [repeated]
  ExtraVal: number [repeated]
  ExtraKeyStr: string [repeated]
  ExtraValStr: string [repeated]
  IsClearExtraBefore: byte

-- === c_league_tech_shop_discount ===
  LeagueId: number
  DiscountGoodsList: number [repeated]

-- === s_act_eye_sight_enter ===
  Id: byte

-- === c_userinfo_other ===
  Info: userinfo_other

-- === c_flipcard_update_pathway ===
  Id: byte
  Progress: number
  State: byte

-- === c_scene_play_drama ===
  DramaName: string
  Loop: number

-- === s_zhanling_get_reward ===
  Id: number
  RewardType: byte

-- === c_card_lock ===
  Uid: number
  IsLock: byte

-- === s_scene_jump ===
  sceneId: number
  x: number
  y: number
  confirm: byte

-- === s_monthly_card_sign ===
  Id: number

-- === c_mail_get_attach ===
  iMailId: number

-- === c_secret_area_cycle_record ===
  PreviousRecord: secret_area_record [repeated]
  HaveRecord: byte
  CurrentRecord: secret_area_record [repeated]

-- === s_league_boss_panel ===
  LeagueId: number
  NeedReward: byte

-- === c_team_new ===
  TeamInfo: team_info

-- === s_act_team_quit ===

-- === c_secret_area_players ===
  PlayerList: secret_area_player [repeated]

-- === s_toplist_page ===
  ID: byte
  SubName: number
  PageNum: number
  IsCross: number

-- === s_top_broadcast_secret_rangeId ===
  GroupIds: number [repeated]

-- === s_league_invite_done ===
  SourceUid: number
  Result: byte

-- === s_rogue_save ===
  Index: number
  Name: string

-- === s_battlefield_pk_ready ===
  List: number [repeated]

-- === c_battlefield_solo_info ===
  AchieveList: {  [repeated]
    Id: number
    Value: number
    State: byte
  }

-- === s_act_boss_challenge_join ===
  HeroUid: number

-- === c_act_sport_race_info ===
  ActId: number
  List: {  [repeated]
    Id: number
    Count: number
  }

-- === s_world_task_reward_rate ===
  Rate: byte

-- === s_danmu_get_total_amount ===
  iType: number
  iPlotId: number

-- === c_rogue_pass_end ===
  PassId: number
  Result: number
  ScoreDetail: number [repeated]
  InnerCoin: number
  GlobalCoin: number
  NextHide: number
  AttachCard: number

-- === s_stage_achievement_info ===
  IdList: number [repeated]

-- === s_fenshen_end ===
  IsFinish: byte

-- === c_act_hero_bp_update ===
  ActId: number
  Active: byte
  List: {  [repeated]
    Id: number
    State: byte
  }
  RewardList: stage_reward [repeated]

-- === s_home_unlock ===
  Floor: byte

-- === c_act_double_resource_info ===
  ActId: number
  RemainCount: number

-- === c_campaign_trigger_on_map_update ===
  FieldId: number
  ChangeTrigger: number
  AddTrigger: number [repeated]
  RemoveTrigger: number [repeated]

-- === c_league_tech_shop_buy ===
  LeagueId: number
  NewSessionId: dword
  GoodsId: number
  BuyCount: byte

-- === s_stage_report ===
  Id: number
  Result: byte
  MaxCombo: number
  ComboDmg: number
  AllDmg: number
  OnHitNum: number
  SoloBossNum: number
  MonsterNum: {  [repeated]
    MonsterId: number
    Amount: number
  }
  HostageNum: {  [repeated]
    HostageId: number
    Amount: number
  }
  ItemNum: {  [repeated]
    ItemId: number
    Amount: number
  }
  EndReport: {
    ClientEndTime: number
    RoundEndType: number
    RoundTimeUse: number
    SkillLevel: {  [repeated]
      SkillId: number
      SkillLevel: number
    }
    RoundFighterMoveTotal: number
    RoundFighterButtonClickCountATK: number
    RoundFighterButtonClickCount1: number
    RoundFighterButtonClickCount2: number
    RoundFighterButtonClickCount3: number
    RoundFighterButtonClickCount4: number
    RoundFighterButtonClickCount5: number
    RoundFighterButtonClickCount6: number
    RoundFighterButtonClickCount7: number
    RoundFighterButtonClickCount8: number
    RoundFighterButtonClickCount9: number
    RoundFighterButtonClickCount10: number
    RoundFighterDpsCount: number
    RoundFighterAtkMissTotal: number
    RoundFighterPlayerCritCount: number
    RoundFighterDamage1Max: number
    RoundFighterDamage1Min: number
    RoundFighterDamage2Max: number
    RoundFighterDamage2Min: number
    RoundFighterDpsTotal: number
    RoundFighterATKMax: number
    RoundFighterATKMin: number
    RoundFighterCritATKMax: number
    RoundFighterCritATKMin: number
    RoundFighterAtkTag: number
    RoundFighterAtkCount: number
    RoundFighterAtkTotal: number
    RoundFighterInitHP: number
    RoundFighterHealHPCount: number
    RoundFighterHealHPMax: number
    RoundFighterHealHPMin: number
    RoundFighterHealHPTotal: number
    RoundFighterDamageHPCount: number
    RoundFighterDamageHPMax: number
    RoundFighterDamageHPMin: number
    RoundFighterDamageHPTotal: number
    RoundFighterEndHP: number
    RoundFighterEndHPPercent: number
    RoundFighterDeadCount: number
    RoundFighterReliveCount: number
    RoundFighterUseHpBotCount: number
    RoundFighterUseHpBotMax: number
    RoundFighterUseHpBotMin: number
    RoundFighterUseHpBotTotal: number
    RoundFighterBeHitCount: number
    RoundFighterBeHitExemptionCount: number
    RoundFighterSpeedMax: number
    RoundFighterSpeedAverage: number
    RoundFighterComboMax: number
    RoundFighterComboCount: number
    RoundFighterComboTimeMax: number
    MonsterCount: number
    MonsterEndCount: number
    MonsterCount1: number
    MonsterCount2: number
    MonsterCount3: number
    BossCount: number
    BossKillCount: number
    HeroDodgeCount: {  [repeated]
      HeroClassId: number
      Count: number
    }
    HeroUltimateSkill: {  [repeated]
      HeroClassId: number
      Count: number
    }
  }

-- === c_frame_fighter_data ===
  Uid: number
  X: number
  Y: number
  Face: number
  Camp: number
  Name: string
  Level: number
  StageLevel: number
  Exp: number
  HeroId: number
  CardUid: number
  Fighting: number
  AvatarId: number
  AvatarFrameId: number
  RobotId: number
  Heros: {  [repeated]
    Mid: number
    HeroId: number
    ShapeId: number
    FashionId: number
    PeakAttrId: number
    Infos: {  [repeated]
      key: byte
      value: number
    }
    CardSkillLevel: {  [repeated]
      SkillId: number
      SkillLevel: number
    }
    CardSpecLevel: {  [repeated]
      SpecId: number
      SpecLevel: number
    }
    RuneSpecList: {  [repeated]
      SpecId: number
      SpecLevel: number
    }
    Buffs: {  [repeated]
      Id: number
      Value: number
    }
    AttachedCardBuff: {  [repeated]
      Id: number
      Lv: number
      Uid: number
    }
    ActiveCards: {  [repeated]
      ItemId: number
      Quality: number
      EnhanceLv: number
      UseTimes: number
    }
    SupportSkill: {  [repeated]
      Index: byte
      HeroId: word
      ShapeId: number
      FashionId: number
    }
  }
  EquipHideAttr: {  [repeated]
    Id: number
    Value: number
  }
  CampaignBuffArgs: {  [repeated]
    Id: number
    Value: number [repeated]
  }
  GroupBuffs: {  [repeated]
    Id: number
    Value: number
  }

-- === c_gem_bag_new ===
  item: special_item_info [repeated]

-- === c_usj_get_end_reward ===

-- === c_home_send_all_home_data ===
  PeopleDataList: home_people_data [repeated]
  CheckinList: home_checkin_list [repeated]
  AllFloorData: home_floor_furniture [repeated]
  FloorUnlock: byte [repeated]
  FloorName: {  [repeated]
    Floor: number
    Name: string
  }

-- === c_card_go_to_fight ===
  CardUid: number
  IsShow: byte

-- === c_campaign_property_add ===
  CampaignId: number
  Property: {  [repeated]
    PropertyId: number
    Count: number
  }

-- === s_battlefield_task_replace ===
  Index: byte

-- === c_interaction_from_other ===
  Type: byte
  EmoticonId: number
  Uid: number

-- === c_act_periodic_task_update ===
  Score: number

-- === s_area_event_reset_stage_times ===
  StageId: number
  Cost: number [repeated]

-- === c_crosspvp_hot ===
  HotInfo: {  [repeated]
    Rank: number
    CWin: number
    CFight: number
    AvatarId: dword
    AvatarFrameId: dword
    Name: string
    HostId: number
    TbPos: crosspvp_pos [repeated]
  }

-- === s_task_submit ===
  task_id: number

-- === c_comment_delreply ===
  CommentId: number
  SenderUid: number
  CommentIdx: number
  ReplyIdx: number
  ReplyUid: number

-- === s_welfare_strength_supply ===
  Id: number

-- === c_stage_back_finish ===

-- === c_league_simple_info ===
  LeagueId: number
  LeagueMoney: number
  LeagueName: string
  Job: byte

-- === s_league_log ===
  LeagueId: number
  LeagueLogNo: number

-- === c_level_up ===
  OldLv: number
  Level: number
  Time: number

-- === c_group_team_kick ===
  GroupId: number
  TargetUid: number

-- === s_home_floor_lvup ===
  Floor: number
  Lv: number

-- === s_equip_attr_switch ===
  FromEquipUid: number
  FromAttrIndex: byte
  ToEquipUid: number
  ToAttrIndex: byte

-- === c_mail_get_list ===
  iVersion: number
  arrMailSimpleInfos: mail_simple_info [repeated]
  iIsFinish: byte

-- === c_offlinepvp_info ===
  CulCount: number
  CulTime: number
  CulSumTime: number
  RankId: number
  TopRankId: number
  RewadRankId: number
  Chance: number
  BuyTimes: number
  Rivals: offlinepvp_rival [repeated]
  Promote: offlinepvp_rival [repeated]

-- === s_userinfo_birthday_hide ===
  Hide: byte

-- === s_emergency_sync ===

-- === c_task_enter_stage ===
  IsEnter: byte

-- === c_share_reward ===
  Id: number

-- === s_crosspvp_ace ===
  Season: dword [repeated]

-- === c_stage_achievement_info ===
  AchievementList: {  [repeated]
    Id: number
    State: byte
  }

-- === c_league_pvp_apply ===
  IsApply: number

-- === c_stage_activity_reward ===
  Id: number

-- === s_league_appoint ===
  LeagueId: number
  TargetUid: number
  Job: byte

-- === c_friend_send_msg ===
  Uid: number
  Name: string
  Icon: number
  Frame: number
  ChatFrame: number
  Level: number
  TopLevel: number
  AUid: number
  Time: number
  Msg: string
  ItemLinks: string

-- === c_chaos_settle ===
  WinCamp: number
  AddScore: number
  NowScore: number
  IsPassive: number
  Info: {  [repeated]
    Name: string
    Camp: number
    AvatarId: number
    AvatarFrameId: number
    HeroId: number
    Kill: number
    Death: number
    ComboKill: number
    TotalHurt: number
    HurtRate: number
  }

-- === c_act_team_task ===
  Task: {  [repeated]
    Id: byte
    Value: number
    State: byte
  }

-- === s_crosspvp_note ===

-- === s_stage_theater ===
  StageId: number
  Extra: {
    HeroUid: number
  }
  Result: number
  Score: number [repeated]
  DramaFinish: number [repeated]

-- === s_usj_enter_stage ===
  ZoneId: number
  PointId: number
  HeroUid: number

-- === c_world_task_ignore_auto_finish_tips ===
  Flag: number

-- === c_group_channel_load ===
  GroupId: number
  ChannelId: number
  Load: number

-- === c_peak_battle_group_champion ===
  IsMeet: byte
  ChampionData: peak_rank_data
  MyPeakRecords: peak_prize_record

-- === s_attached_card_reset ===
  TargetUid: number

-- === c_pay_info_end ===
  shopid: number [repeated]

-- === s_platform_access_friend_share_invite_reward ===
  RewardId: number

-- === s_night_fight_enter_fight ===
  StageId: number
  HeroUid: number

-- === c_act_secret_info ===
  ActId: number
  CurScore: number
  RewardTakeList: number [repeated]
  LevelRangeId: number

-- === c_league_about ===
  LeagueId: number
  LeagueInfo: {
    LeagueName: string
    HeadIcon: number
    HeadFrameIcon: number
    Lv: byte
    Exp: number
    Notic: string
    Ad: string
    MemberAmount: word
    OnlineMemberAmount: word
    ApplyAmount: byte
    Money: number
    CreateTime: dword
    WeekGongXun: number
    ChangeNameCardAmount: number
    LastRank: number
    BossTime: dword
    BossDamage: number
    BossRewardList: number [repeated]
    ChallengeTimes: number
    AddChallengeTimes: number
  }
  Job: byte

-- === c_fenshen_start ===
  ActiveID: number
  Result: byte [repeated]

-- === s_userinfo_location ===
  Location: string

-- === c_time_sync ===
  TimeZone: number
  CurTime: number
  NewServerTime: number

-- === c_act_consume_info ===
  ActId: number
  Series: {  [repeated]
    Id: number
    State: byte
  }
  List: number [repeated]

-- === s_grid_box_reset ===
  ActId: number
  times: number

-- === s_platform_access_friend_share ===

-- === c_act_sport_race_result ===
  ActId: number
  Id: number
  Count: number
  RewardList: {  [repeated]
    AddLog: stage_reward [repeated]
  }

-- === c_peak_battle_pick_hero ===
  HeroCIdList: number [repeated]

-- === c_shot_info ===
  Point: number
  IsGet: byte

-- === c_battlefield_matched ===
  Uid: number
  Name: string
  Rank: number
  ShapeId: number
  MercenaryList: number [repeated]
  TotalNum: number
  WinNum: number
  Location: string

-- === s_card_feed ===
  CardUid: number
  ItemList: item_data [repeated]

-- === c_friend_choose ===
  Infos: friendinfo [repeated]

-- === s_league_buy_boss_challenge_times ===
  Times: number

-- === c_night_fight_fight_over ===
  StageId: number
  IsWin: number

-- === s_battlefield_stmatch ===
  type: number
  MercenaryIdList: number [repeated]

-- === c_league_active_star ===
  LeagueId: number
  ActiveStarInfo: {  [repeated]
    Uid: number
    Name: string
    HeadIcon: number
    HeadFrameIcon: number
    WeekGongXun: number
  }

-- === c_crosspvp_open_time ===
  OpenTime: number

-- === c_group_all_finish_loading ===

-- === c_battlefield_task_info ===
  IsFightOver: byte
  IsGetDayReward: byte
  IsGetWeekReward: byte
  ReplaceTimes: byte
  FreshenTime: number
  Tasks: battlefield_task [repeated]

-- === s_frame_correct ===
  Uid: number
  ClientCurUid: number
  CFrame: number
  Data: {  [repeated]
    AtrType: byte
    Uid: number
    Id: number
    Value: number [repeated]
    EString: string [repeated]
  }

-- === c_stage_finish_loading ===
  Uid: number

-- === s_league_tech_modify_sign ===
  LeagueId: number
  Sign: string

-- === s_teach_finish ===
  HeroCId: number
  SkillList: {  [repeated]
    SkillId: number
    Count: number
  }

-- === c_league_tech_tree_panel ===
  WeekNo: number
  DayNo: number
  LeagueId: number
  JoinWeekTechId: number
  HeroClass: number
  JoinTime: dword
  TechNotic: string
  TechList: number [repeated]
  WeekTechList: {  [repeated]
    WeekTechId: number
    JoinCount: byte
    Progress: number
    Time: number
    ProgressInfo: {  [repeated]
      Percent: byte
      Time: dword
    }
    EventList: {  [repeated]
      EventId: number
      CurLeagueLv: byte
      StartTime: dword
      EndTime: dword
      DealTimes: byte
      IsReward: byte
    }
  }
  PreBuyList: number [repeated]
  RewardList: number [repeated]

-- === c_league_modify_notic ===
  LeagueId: number
  Notic: string

-- === s_team_add_robot ===
  Robot: robot_info [repeated]

-- === s_interaction_config_add ===
  Type: byte
  EmoticonId: number
  Index: number
  HeroId: number

-- === s_fenshen_aid_reward ===
  AidRewardId: number

-- === c_group_team_member_ready ===
  GroupId: number
  Uid: number
  Result: byte

-- === s_attached_card_compose ===
  ACardUids: number [repeated]

-- === c_battlefield_pk_handle_ret ===

-- === c_chat_private ===
  Uid: number
  Name: string
  TypeId: number
  Level: number
  TopLevel: number
  Msg: string
  Links: string
  SendTime: number
  ReceiverUid: number

-- === s_login_player_enter ===
  id: number

-- === s_league_board_public ===
  LeagueId: number
  Msg: string

-- === s_rogue_inner_benefit_info ===

-- === c_group_enter_area ===
  Uid: number
  AreaId: number

-- === c_comment_list ===
  CommentId: number
  SIdx: number
  EIdx: number
  List: commentinfoex [repeated]
  UserList: commentinfo [repeated]

-- === s_client_shader ===
  Name: string
  MacroStr: string

-- === c_office_info ===
  Favor: number
  HeroStep: number
  Active: number
  PickDaily: {  [repeated]
    Index: number
    State: byte
    Values: number [repeated]
  }
  PickStep: {  [repeated]
    Index: number
    State: byte
    Value: number
  }
  PickActive: {  [repeated]
    Index: number
    State: byte
  }
  PickWeekly: {  [repeated]
    Index: number
    State: byte
    Values: number [repeated]
  }
  LevelStep: byte
  PickGuides: {  [repeated]
    Index: number
    Value: number
    AllValue: number
  }

-- === c_welfare_exchange_money ===
  Type: byte
  Count: number
  Exchange: number
  TypeCount: number
  BoneCount: number

-- === s_usj_server_score ===

-- === c_avatar_info ===
  UsingAvatar: number
  UsingAvatarFrame: number
  AvatarInfo: number [repeated]
  AvatarFrameInfo: number [repeated]

-- === c_attached_card_enhance ===
  ACardUid: number
  EnhanceLv: number

-- === s_scene_climbing ===
  Climbing: climbing

-- === c_league_pvp_fight_data ===
  WinLeagueId: number
  OverScores: number [repeated]
  MemberPvpData: league_pvp_member_fight_data [repeated]

-- === c_group_back_channel ===

-- === c_login_cdkey ===

-- === c_secret_area_cycle ===
  CycleTypeId: number
  SeasonId: number
  CycleId: number
  PersonalityGroupId: number
  EndTime: number

-- === c_softball_throw ===
  Power: number
  Angle: number
  Range: number

-- === c_login_wait ===
  pos: number
  total: number
  leftTime: number

-- === s_userinfo_location_hide ===
  Hide: byte

-- === s_title_getreward ===
  Id: number

-- === s_league_pvp_fight_data ===

-- === s_act_exercise_start ===
  ActId: number
  Id: number
  HeroList: {  [repeated]
    Index: number
    HeroCId: number
  }

-- === s_league_pvp_pk ===
  RivalUid: number
  ResourceId: number

-- === s_peak_battle_fight_log ===
  LogType: number

-- === s_chat_frame_use ===
  Id: number

-- === s_lantern_start ===

-- === s_act_daily_stage_choose ===
  ActId: number
  StageId: number

-- === c_group_team_info ===
  GroupId: number
  Embattle: number [repeated]
  MemberList: group_member_base_info [repeated]

-- === s_interaction_use_mood ===
  MoodId: number

-- === s_act_goods_buy ===
  ActId: number
  GoodsId: number

-- === s_custom_gift_trigger ===
  Id: number
  Cond: number [repeated]

-- === s_item_select_reward ===
  ItemId: number
  Select: number [repeated]
  Amount: number
  NowAmount: number

-- === s_peak_battle_support_info ===

-- === c_userinfo_badge_set ===
  Badge: byte [repeated]

-- === c_offlinepvp_replace ===
  Rivals: offlinepvp_rival [repeated]
  Promote: offlinepvp_rival [repeated]

-- === c_world_task_auto_finish ===
  IsSuccess: number

-- === c_usj_get_point_reward ===
  ZoneId: number
  RewardList: {  [repeated]
    PointId: number
    Reward: stage_reward [repeated]
  }

-- === c_reconnect_flag ===
  Falg: number

-- === s_group_team_list ===
  ChannelId: number

-- === s_growth_fund_info ===

-- === c_card_show_oper ===
  Id: number

-- === c_league_tech_event_finish ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte
  EndTime: dword

-- === c_league_board_comment_oper ===
  LeagueId: number
  BoardId: number
  CommentId: number
  CommentCount: number

-- === c_server_frame ===
  FrameId: number
  FrameData: {  [repeated]
    Cmd: number [repeated]
  }

-- === c_herochip_stage_sync_data ===
  DailyTimes: {  [repeated]
    Id: number
    Times: number
  }
  PassStage: number [repeated]

-- === c_group_wanfa_id ===
  WanFaId: number

-- === c_total_recharge_info ===
  Total: number
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === c_peak_battle_primary_ready_cd ===
  Time: number

-- === c_world_task_info ===
  FinishList: {  [repeated]
    Map: number
    Area: number
    TaskId: number
  }
  OpenWorldMap: {  [repeated]
    MapId: number
  }
  PrestigeMap: number
  PrestigeTaskStatus: byte
  IsFirstRewardSign: byte
  RewardBase: byte
  ExtraReward: {  [repeated]
    ItemId: number
    Num: number
    TaskId: number
    Type: byte
  }
  IgnoreAutoFinishTips: byte

-- === s_welfare_sign ===
  SignType: byte

-- === s_team_clear_apply ===

-- === c_team_kick_leader ===
  Time: number

-- === s_secret_area_history ===

-- === c_act_exlottery_draw ===
  DrawId: number
  Times: byte
  RewardList: {  [repeated]
    AddLog: stage_reward [repeated]
    IsImportant: byte
  }
  GuaranteeInfo: {  [repeated]
    GuaranteeId: number
    DrawNum: number
  }

-- === c_relax_stage_sync_cond ===
  NewData: {  [repeated]
    Type: byte
    Id: number
    Status: number
    Reward: number
  }

-- === s_league_board_list ===
  LeagueId: number
  PageNum: number [repeated]

-- === s_pay_item ===
  ShopId: number
  GoodsId: number
  Price: number
  Amount: number

-- === c_home_unlock ===
  Floor: byte

-- === s_office_pick_active ===
  Index: number

-- === s_act_team_accept ===
  Uid: number

-- === s_chat_private ===
  target_uid: number
  msg: string
  ItemLinks: string

-- === c_task_info ===
  tasks: taskinfo [repeated]
  finishs: number [repeated]
  IsStart: number
  IsEnd: number

-- === c_comment_comment ===
  CommentId: number
  CommentInfo: commentinfo

-- === s_card_lock ===
  Uid: number
  IsLock: byte

-- === s_secret_area_active_key ===

-- === s_business_extend_get_reward ===
  day: number
  index: number

-- === c_offlinepvp_money ===
  CulCount: number
  CulTime: number
  CulSumTime: number

-- === c_act_seven_day_buy ===
  ActId: number
  GoodsId: number

-- === c_card_lock_skill ===
  HeroCId: number
  Index: byte
  IsLock: byte

-- === c_hero_class_info ===
  Idx: byte
  Id: number
  Value: number
  State: byte
  SkipCount: byte

-- === c_userinfo_tag_set ===
  Tag: byte [repeated]

-- === s_campaign_task_accept ===
  Id: number

-- === s_area_event_enter_stage ===
  StageId: number
  HerosUId: number [repeated]

-- === c_offlinepvp_wipe ===
  Reward: {  [repeated]
    RewardList: stage_reward [repeated]
  }

-- === c_equip_send_equip_hole_info ===
  HoleList: {  [repeated]
    EquipPos: byte
    EnhanceLv: byte
    FailCount: number
    BreakLv: byte
    StarLv: byte
    RemouldLv: byte
    RemouldProgress: dword
    DiesetLv: byte
    DiesetProgress: dword [repeated]
  }

-- === s_skill_get_spec_level_list ===
  HeroUidList: number [repeated]

-- === c_night_fight_reward ===
  FixedReward: stage_reward [repeated]
  ExtraReward: stage_reward [repeated]
  SpecialReward: stage_reward [repeated]

-- === c_userinfo_info ===
  Info: userinfo

-- === c_group_team_friend_list ===
  GroupId: number
  FriendList: group_member_base_info [repeated]

-- === c_secret_area_times ===
  DayIncomeTimes: number
  CycleIncomeTimes: number

-- === c_recharge_info ===
  RechargeCount: number
  RechargeValue: number
  RechargeGold: number

-- === s_role_change_name ===
  Name: string
  Free: byte
  ItemNum: number

-- === s_hero_rank_info ===

-- === c_friend_del ===
  Type: number
  Uid: number

-- === c_team_invite ===
  TargetUid: number

-- === c_all_server_cond_team_info ===
  ServerCondInfo: {  [repeated]
    Id: number
    Status: byte
    TeamList: {  [repeated]
      TeamName: string
      Time: number
      CaptainUid: number
      MemberList: {  [repeated]
        Uid: number
        Name: string
        AvatarId: byte
        AvatarFrameId: byte
        GameSvrId: number
      }
    }
  }

-- === s_league_pvp_resource_occupy ===
  ResourceId: number
  OccupyPos: number

-- === c_league_tech_buff_update ===
  BuffList: {  [repeated]
    BuffId: number
    BuffLv: byte
  }

-- === c_group_npc_info ===
  Hp: number
  Time: number

-- === s_league_member_list ===
  LeagueId: number

-- === c_league_join_boss ===

-- === c_offlinepvp_ready ===
  RankId: number
  Fighting: number
  DefPos: offlinepvp_hero_pos [repeated]

-- === s_recharge_reward_total_get ===
  Id: number

-- === s_usj_get_stage_record ===
  ZoneId: number
  PointId: number

-- === s_team_acc_invite ===
  TeamUid: number

-- === s_attached_card_book ===

-- === s_home_checkin_update ===
  UpdateList: {  [repeated]
    Floor: byte
    RoleId: number [repeated]
  }

-- === c_rogue_inner_benefit_info ===
  Data: {  [repeated]
    Uid: number [repeated]
    BuffIds: number [repeated]
  }

-- === c_act_hero_bp_info ===
  ActId: number
  Active: byte
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === s_league_tech_shop_buy ===
  LeagueId: number
  SessionId: dword
  GoodsId: number

-- === s_frame_md_check ===
  Uid: number
  CurFrame: number
  Md5: string

-- === c_item_new ===
  item: special_item_info [repeated]

-- === s_home_role_interact ===
  RoleId: number
  InteractType: number

-- === c_group_captain_alter ===
  AreaId: number
  Index: number
  TeamId: number

-- === s_frame_refresh ===
  Uid: number
  UserUid: number

-- === s_group_team_info ===
  GroupId: number

-- === s_group_team_kick ===
  GroupId: number
  TargetUid: number

-- === c_act_hero_license_info ===
  Lv: byte
  Exp: number
  Reward: byte
  PayRewardLv: byte
  IsHeroLicense: byte
  CurWeekExp: word
  GoodsHaveBrought: {  [repeated]
    Id: number
    Num: number
  }

-- === c_base_station_all_info ===
  iClientVersion: number
  arrFinishAidCount: {  [repeated]
    iType: number
    iCount: number
  }
  arrBaseStationInfo: base_station_info [repeated]

-- === c_emergency_result ===
  Players: {  [repeated]
    Uid: number
    TrueItem: item_data [repeated]
    FakeItem: item_data [repeated]
    ExtraItems: extra_item_data [repeated]
    LeagueItems: stage_reward [repeated]
    Dps: number
    MaxCombo: number
    Reborn: number
    LeagueDraw: byte
  }
  MvpUserUid: number
  WasteTime: number

-- === c_team_be_invite ===
  InviteInfo: team_invite_info

-- === s_league_pvp_view_pvp_records ===
  IsRival: number

-- === s_league_board_mine ===
  LeagueId: number

-- === c_friend_quick_deal_with_apply ===

-- === s_usj_enter_activity_ui ===

-- === c_mail_quickly_get_attach ===
  arrMailIds: number [repeated]

-- === c_group_team_apply_done ===
  GroupId: number
  TargetUid: number
  Result: byte

-- === s_home_floor_furniture ===
  Floor: number
  DelDecoration: number [repeated]
  AddDecoration: number [repeated]
  DelFurniture: number [repeated]
  AddFurniture: {  [repeated]
    Tid: string
    FurnitureId: number
    X: number
    Y: number
    Z: number
    Face: number
    WallIndex: number
  }
  MoveFurniture: {  [repeated]
    Uid: number
    X: number
    Y: number
    Z: number
    Face: number
    WallIndex: number
  }

-- === c_group_report_data ===
  Type: number

-- === s_hero_class_stage ===
  Idx: byte
  HeroCId: number

-- === s_resource_stage_enter ===
  Id: number
  HeroUid: number

-- === c_team_need_to_leave ===
  StageId: number

-- === c_team_change_extra ===
  ExtraIndex: number [repeated]
  ExtraVal: number [repeated]

-- === c_usj_unlock_zone ===
  ZoneId: number
  Reason: number

-- === s_share_reward ===
  Id: number

-- === s_team_quick_chat ===
  Index: number

-- === s_league_get_rank_simple_info ===
  LeagueId: number [repeated]

-- === c_league_pvp_report ===
  WinUid: number
  NList: number [repeated]
  SList: string [repeated]

-- === c_avatar_frame_use ===
  Id: number

-- === c_fashion_update ===
  List: {  [repeated]
    Id: number
    State: byte
    EndTime: number
  }

-- === c_league_tech_pre_buy ===
  LeagueId: number
  WeekTechId: number
  Result: byte

-- === c_act_allsvr_stage_update_level ===
  ActId: number
  AreaInfo: {
    Id: number
    RewardList: stage_reward [repeated]
    LevelList: {  [repeated]
      Id: number
      Count: number
    }
  }

-- === c_act_rank_reissue ===
  ActId: number
  List: number [repeated]

-- === c_act_lottery_info ===
  Info: {  [repeated]
    DropId: number
    DropTimes: number
    LeftDropTimes: number
    Items: {  [repeated]
      Item: number
      Times: number
    }
  }

-- === c_fenshen_option ===
  Option: byte
  Result: byte

-- === c_peak_battle_get_task_reward ===
  TaskId: number

-- === s_peak_battle_wonder_play ===
  BattleType: number

-- === s_sugar_room_make_cake ===
  MenuId: number
  Count: number

-- === s_sugar_room_exchange_count ===

-- === s_welfare_exchange_money ===
  Type: byte
  Times: number

-- === s_task_sync_info ===
  TaskId: number
  Type: string
  ParamList: string [repeated]

-- === c_zhanling_task_update ===
  ActId: number
  TaskList: {  [repeated]
    Id: number
    Status: byte
    Val: number
  }

-- === s_home_like ===
  Uid: number
  LikeOrCancel: byte

-- === s_frame_lag_report ===
  Data: {  [repeated]
    CurFrame: number
    FrameNum: number
    Time: number
  }
  IsFinish: byte

-- === c_act_eye_sight_update ===
  Id: byte
  State: byte

-- === c_mail_have_new_mail ===
  arrNewMailInfo: {  [repeated]
    iMailId: number
    iTimeOut: number
  }

-- === c_replay_check ===

-- === s_stage_playback ===
  StageUid: number
  CurGroup: number
  WanFaId: number
  NumberList: number [repeated]
  StringList: string [repeated]

-- === s_team_auto_acc ===
  AutoAcc: number

-- === c_secret_area_key ===
  Status: byte
  KeyId: number
  StageId: number
  LevelRangeId: number

-- === c_attached_card_compose ===
  IsSuccess: number

-- === s_rogue_pass_hero ===
  HeroIndex: number

-- === s_card_go_to_fight ===
  CardUid: number
  IsShow: byte

-- === c_friend_send_strength ===
  TargetUid: number

-- === c_friend_update_str ===
  Uid: number
  Infos: {  [repeated]
    Key: byte
    Value: string
  }

-- === c_usj_get_stage_record ===
  StageRecords: {  [repeated]
    PointId: number
    UserUid: number
    UserName: string
    UserLevel: number
    HeroId: number
    Fighting: number
    Score: number
  }

-- === c_item_amount ===
  ItemList: normal_item_info [repeated]

-- === s_secret_area_task_reward ===
  TaskId: number

-- === c_act_start ===
  ActData: {
    ActId: number
    ActType: number
    StartTime: number
    EndTime: number
    SyncInfo: string
  }

-- === c_chaos_match ===
  MatchType: number

-- === c_rogue_pass_difficult ===
  Difficult: number

-- === c_league_pvp_resource_change ===
  ResourceData: league_pvp_resource_data [repeated]

-- === c_toplist_pages ===
  ID: byte
  SubName: number
  PageNums: number [repeated]
  MaxPageNum: number
  SelfUid: number
  Pages: {  [repeated]
    PageNum: number
    Page: top_rank_data [repeated]
  }
  SelfRankInfo: top_rank_data
  IsCross: number

-- === c_league_tech_modify_shop_manager_sign ===
  LeagueId: number
  ManagerSign: string

-- === c_act_pickbox_info ===
  ActId: number
  PoolId: number
  AllGet: byte
  FreeCount: byte
  ItemList: {  [repeated]
    Id: number
    GetNum: number
  }

-- === c_guide_id_done ===
  GuideId: number
  Idx: number

-- === s_league_tech_progress_reward ===
  LeagueId: number
  WeekTechId: number
  RewardId: number [repeated]

-- === c_hero_rank_stage_update ===
  Id: number
  Star: byte [repeated]

-- === c_lottery_draw ===
  DrawId: number
  Times: number
  OneTimes: number
  TenTimes: number
  RewardList: {  [repeated]
    AddLog: stage_reward [repeated]
    IsImportant: byte
  }
  GuaranteesInfo: {  [repeated]
    GuaranteesType: number
    ProcessInfo: {  [repeated]
      ImportantId: number
      AccumulationTimes: number
    }
  }

-- === s_rogue_chg_record_name ===
  Index: number
  HeroIndex: number
  Name: string

-- === c_rune_rabbet_info ===
  RuneRabbetList: rune_rabbet_info [repeated]
  OverLoadInfo: {  [repeated]
    HeroCId: word
    HoldLv: byte [repeated]
  }

-- === s_achieve_getreward ===
  Id: number

-- === c_new_hero_info ===
  StageId: number [repeated]
  ActId: number

-- === c_home_role_mood_list ===
  Data: home_role_mood [repeated]

-- === c_battlefield_pk_quit ===

-- === s_usj_stage_restart ===
  ZoneId: number
  PointId: number
  HeroUid: number

-- === c_task_sync_info ===
  TaskId: number
  Type: string
  ParamList: string [repeated]

-- === s_secret_area_finish_stage ===
  Members: {  [repeated]
    UserUid: number
    HurtSum: number
  }
  MvpUserUid: number

-- === c_act_team_reward ===
  State: byte [repeated]
  Point: number

-- === s_secret_area_drop_card ===
  CardPos: number

-- === s_league_search ===
  LeagueNameOrId: string

-- === c_group_scene_info ===
  CreateTime: number
  Phase: number
  BossList: {  [repeated]
    BossHp: number
    Shield: number
  }
  MapsList: {  [repeated]
    AreaId: number
    MapList: group_map_data [repeated]
  }
  Display: number
  AreasUser: {  [repeated]
    AreaId: number
    AreaUser: number [repeated]
  }

-- === s_card_show_oper ===
  Id: number

-- === c_rune_attr_info ===
  RuneAttrList: rune_attr_info

-- === c_act_end ===
  ActId: number
  ActType: number

-- === c_sendprize_exchange_count ===
  ExchangeCount: {  [repeated]
    Index: number
    Count: number
  }

-- === c_common_protocol ===
  Action: number
  JsonArgs: string

-- === s_fenshen_\018ption ===
  Option: byte

-- === s_exchange_do ===
  ItemId: number

-- === c_stage_drop ===
  Monster: stage_drop_list_reward [repeated]
  Boss: stage_drop_list_reward [repeated]
  StagePassDrop: stage_drop_list_reward [repeated]
  Card: stage_drop_list_reward [repeated]
  VipCard: stage_drop_list_reward [repeated]
  FirstReward: stage_drop_list_reward [repeated]

-- === c_act_client_trigger_update ===
  ActId: number
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === c_monthly_card_info ===
  CardInfo: {  [repeated]
    Id: number
    ActiveTime: number
    Days: number
    LastGetTime: number
    GetDay: byte [repeated]
  }

-- === s_league_pvp_view_fight ===
  UidList: number [repeated]

-- === s_pay_recharge ===
  Uid: number

-- === c_campaign_cache_update ===
  CampaignId: number
  HasCache: byte

-- === c_peak_primary_rival_refuse ===

-- === c_task_trigger_sync ===
  Uid: number

-- === c_pressure_like ===
  Success: byte
  Uid: number

-- === c_evaluate ===

-- === c_team_recruit ===

-- === c_secret_area_time_record ===
  List: {  [repeated]
    Tag: string
    TeamUid: number
  }

-- === s_battlefield_task_info ===

-- === c_league_tech_buff_clear ===

-- === s_group_boss_hp ===
  FrameId: number
  BossHp: number

-- === c_group_team_join ===
  GroupId: number
  Pos: byte
  MemberInfo: group_member_info

-- === c_platform_access_friend_share_daily_reward ===
  DailyRewardStatus: byte

-- === c_friend_info ===
  Type: number
  Infos: friendinfo [repeated]

-- === s_act_hero_rank ===
  Page: number

-- === c_chat_clean ===
  Uid: number

-- === c_act_monopoly_dice_res ===
  ActId: number
  Number: number
  MysticEventId: number

-- === s_act_eye_sight_result ===
  Id: byte
  Result: byte
  Map: byte [repeated]

-- === s_league_get_team_reward ===
  LeagueId: number
  RewardId: number

-- === c_group_team_new_apply ===
  GroupId: number
  ApplyInfo: group_member_base_info

-- === s_league_apply_list ===

-- === c_gem_bag ===
  page: number
  totalpage: number
  item: special_item_info [repeated]

-- === c_secret_area_all_hero ===
  AllHero: secret_area_hero [repeated]

-- === c_league_tech_modify_sign ===
  LeagueId: number
  Sign: string

-- === c_campaign_internal_status ===
  CampaignId: number
  ControlUid: number
  UserPos: campaign_pos
  TriggerOnMap: {  [repeated]
    FieldId: number
    TriggerList: {  [repeated]
      AreaId: number
      Detected: byte
      See: byte
    }
  }
  HeroInfo: campaign_hero_info [repeated]
  Buff: number [repeated]
  Property: {  [repeated]
    PropertyId: number
    Count: number
  }
  FinishTriggerList: {  [repeated]
    FieldId: number
    TriggerList: number [repeated]
  }
  SelectBuff: number [repeated]
  TaskList: campaign_task_info [repeated]
  FinishTask: number [repeated]
  DramaIndex: number [repeated]

-- === c_frame_report ===
  DataMax: byte
  DataIndex: byte
  CFrame: number
  ReportList: {  [repeated]
    AtrType: byte
    value: number [repeated]
    extval: string [repeated]
  }

-- === c_relax_stage_sync_data ===
  DailyBoxTimes: number
  TotalBoxTimes: number
  DailyRewardTimes: number
  TotalRewardTimes: number
  RoundData: {  [repeated]
    Id: number
    Status: number
    Reward: number
  }
  StepsData: {  [repeated]
    Id: number
    Status: number
    Reward: number
  }

-- === s_offlinepvp_task_reward ===
  TaskId: number

-- === c_league_donate_reward ===
  RewardId: number

-- === c_league_donate_panel ===
  LeagueId: number
  UserDonateTimes: byte
  LeagueDonateTimes: word
  DonateRewardIds: word [repeated]
  LeagueDonateNo: number
  LeagueDonateLogs: {  [repeated]
    iDonateLogId: number
    arrArgs: string [repeated]
    iDonateLogTime: number
    iDonateLogNo: number
  }

-- === s_item_resolve ===
  NormalItemList: normal_item_info [repeated]
  SpecialItemUidList: number [repeated]

-- === s_sendprize_send_prize ===
  HeroId: number
  PrizeCount: number

-- === s_rogue_global_benefit_info ===
  GlobalBuffIds: number [repeated]

-- === s_area_event_trigger_on ===
  AreaId: number

-- === s_league_create ===
  LeagueName: string

-- === s_platform_access_friend_share_join_reward ===

-- === s_peak_battle_task_info ===

-- === c_group_team_league_list ===
  GroupId: number
  LeagueList: group_member_base_info [repeated]

-- === c_frame_init_data ===
  Seed: number
  IsUpd: byte
  No2Uid: {  [repeated]
    No: byte
    Uid: number
  }

-- === c_league_audit_panel ===
  LeagueId: number
  Status: byte
  Lv: byte
  Achieve: number

-- === s_league_tech_event_finish_reward ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte [repeated]

-- === s_campaign_clear_cache ===
  CampaignId: number

-- === s_league_donate ===
  LeagueId: number
  DonateTimes: byte
  LeagueMoneyLogNo: number
  LeagueDonateLogNo: number

-- === s_rune_lock ===
  Uid: number
  Type: number

-- === s_chaos_info ===

-- === s_league_board_oper ===
  LeagueId: number
  BoardId: number
  OperType: byte

-- === s_base_station_uplevel ===
  iBaseStationId: byte

-- === c_card_resonance_reward ===
  RReward: {  [repeated]
    CardUid: number
    Rlv: byte
    Reward: {  [repeated]
      ItemId: number
      Count: number
    }
  }

-- === c_team_apply_leader ===
  Uid: number
  Name: string

-- === s_frame_new_correct ===
  Uid: number
  Frame: number

-- === c_league_pvp_self_occupy ===
  ResourceId: number
  Pos: number
  Time: number

-- === s_skill_get_skill_level ===
  HeroUid: number

-- === s_chaos_ban ===
  HeroClassId: number

-- === s_lottery_choose_up ===
  DrawId: number
  UpRatioId: number

-- === s_collect_check ===
  Id: number

-- === c_secret_area_task_update ===
  TaskList: {  [repeated]
    Id: number
    Status: number
    CurValue: number
  }

-- === s_home_update_role_event ===
  RoleId: number

-- === s_rogue_pass_end ===
  PassId: number
  Result: number
  MaxHp: number
  CurHp: number
  HitTimes: number
  DeadTimes: number
  UseTime: number
  MonsterDamage: number
  AttachCard: number [repeated]

-- === c_userinfo_base ===
  BaseInfo: {  [repeated]
    Uid: number
    Name: string
    Level: byte
    TopLevel: number
    AvatarId: dword
    AvatarFrameId: dword
    Online: byte
    Fighting: number
  }

-- === c_battlefield_reward ===
  Id: number
  NowRank: number
  NewRank: number

-- === c_secret_area_hero_update ===
  HeroList: secret_area_hero [repeated]

-- === c_crosspvp_rank_reward ===
  RankId: number

-- === c_league_pvp_view_base_info ===
  IsRival: number
  LeaguePvpBaseInfo: league_pvp_base_info

-- === c_act_boss_challenge_svr_ach_reward ===
  AchId: number

-- === c_city_level_add_exp ===
  Exp: number

-- === c_share_info ===
  Id: number [repeated]

-- === c_league_pvp_rival_info ===
  RivalInfo: {  [repeated]
    Camp: byte
    Uid: number
    Name: string
    LeagueName: string
    HeroCId: number
    ShapeId: number
    KillCount: number
  }

-- === s_login_cdkey ===
  CDKey: string

-- === s_league_donate_reward ===
  LeagueId: number
  RewardId: number

-- === c_item_normal_list ===
  page: number
  totalpage: number
  item: normal_item_info [repeated]

-- === c_campaign_task_update ===
  TaskInfo: campaign_task_info

-- === c_fenshen_end ===
  IsFinish: byte
  RightTimes: byte
  Rewards: stage_reward [repeated]
  TotalJoinDays: number
  TotalRightTimes: number

-- === c_hero_rank_task_update ===
  List: {  [repeated]
    Id: number
    Value: number
    State: byte
  }

-- === s_team_enter_voice ===
  VoiceId: number

-- === c_funcopen_list ===
  idlist: byte [repeated]

-- === c_offlinepvp_task_reward ===
  TaskId: number

-- === c_act_mini_game_info ===
  ActId: number
  StageList: {  [repeated]
    Id: number
    State: byte
  }
  BoxList: {  [repeated]
    Id: number
    Count: number
  }

-- === s_chaos_choose_hero ===
  HeroClassId: number
  SelectType: number

-- === c_league_board_info ===
  LeagueId: number
  LastPubTime: number
  CDTime: number
  IsNewBoard: number
  BoardUpdate: {  [repeated]
    BoardId: number
    NewComment: number
  }

-- === c_pressure_like_info ===
  ZanList: number [repeated]

-- === c_puzzle_info ===
  List: {  [repeated]
    Id: byte
    Value: number
    State: byte
  }
  TotalReward: byte

-- === s_chaos_match ===
  MatchType: number
  IsGuide: number

-- === s_secret_target_stage ===
  stageId: number

-- === c_task_info_update ===
  action_type: number
  task_info: taskinfo
  Reward: stage_reward [repeated]
  RewardRate: number

-- === c_rogue_benefit_add ===
  AddList: {  [repeated]
    BuffId: number
    IsStage: number
  }
  DelList: {  [repeated]
    BuffId: number
    IsStage: number
  }

-- === s_userinfo_heros ===
  Cid: number [repeated]

-- === c_flipcard_info ===
  Version: number
  Cycle: number
  LastIndx: number
  CurCount: number
  UseCount: number
  PathwayList: {  [repeated]
    Id: byte
    Progress: number
    State: byte
  }
  TotalReward: byte
  CycleReward: byte [repeated]

-- === c_mail_cannot_get_attach ===

-- === c_pay_item_result ===
  ShopId: number
  GoodsId: number [repeated]
  RewardList: stage_reward [repeated]

-- === s_act_team_kick ===
  Uid: number

-- === c_card_hero_bio_info ===
  HeroBiographyList: {  [repeated]
    CardUid: number
    BiographyIdList: number [repeated]
  }

-- === c_campaign_shop_info ===
  ShopId: number
  Buff: {  [repeated]
    Pos: byte
    BuffId: number
  }
  BuyCount: number [repeated]

-- === c_crosspvp_state ===
  Season: number
  state: number

-- === c_pay_recharge ===
  Uid: number

-- === c_base_station_uplevel ===
  mpBaseStationInfo: base_station_info

-- === c_offlinepvp_rank_down ===
  OldRankId: number
  NewRankId: number

-- === c_peak_battle_group_info ===
  Phase: number
  PhaseTime: number
  TeamData: {  [repeated]
    Members: peak_battle_data [repeated]
    PromotionList: {  [repeated]
      GroupId: byte
      Uids: number [repeated]
      PlayBackId: number [repeated]
    }
  }

-- === c_city_level_up ===
  Level: word

-- === c_team_match ===
  MatchVal: number [repeated]

-- === s_equip_on ===
  EquipUid: number

-- === c_welfare_sign ===
  SignType: byte
  FixDay: byte
  SignList: byte [repeated]

-- === c_attached_lot_compose ===
  Star: number
  Cost: number
  ComposeNum: number

-- === c_offline_cache_info ===
  List: {  [repeated]
    Uid: number
    Name: string
    Level: number
    TopLevel: number
    Fighting: number
    ShapeCacheId: number
    HeroId: number
    FaceIcon: number
    FaceFrame: number
  }

-- === c_night_fight_info ===
  StageInfo: {  [repeated]
    NightFightId: number
    Progress: byte
    IsPass: byte
  }

-- === c_skill_level_list ===
  SkillInfoList: skill_level_info [repeated]

-- === c_scene_player_teleport ===
  Uid: number
  X: word
  Y: word
  Face: number
  Effect: number

-- === c_pressure_update ===

-- === s_league_tech_shop_discount ===
  LeagueId: number
  DiscountGoodsList: number [repeated]

-- === s_recharge_reward_info ===

-- === s_league_pvp_set_declaration ===
  Declaration: string

-- === c_attached_card_directional_compose ===
  IsSuccess: number

-- === c_guide_jump ===

-- === s_act_consume_unlock ===
  ActId: number
  Id: number [repeated]

-- === s_hero_rank_stage_end ===
  Id: number
  Star: number [repeated]

-- === c_herochip_red_info ===
  List: number [repeated]

-- === c_pay_bonus ===
  Level: number

-- === s_act_boss_challenge_rejoin ===

-- === c_stage_result ===
  StageId: number
  Result: number
  Time: number
  RewardList: stage_reward [repeated]
  StageInfo: {  [repeated]
    Id: number
    Status: number
    StarList: number [repeated]
    FullStarTime: number
  }

-- === s_battlefield_pk_invite ===
  Uid: number

-- === c_home_floor_furniture ===
  Floor: byte
  Res: byte

-- === s_rogue_buy ===
  Index: number
  Type: number

-- === c_card_seeinfo ===
  Uid: number
  CardInfo: {  [repeated]
    Uid: number
    HeroId: dword
    Lv: word
    Exp: number
    ShapeId: number
    FashionId: number
    Fighting: number
    Satiety: number
    WorkoutLv: byte
    WorkoutItem: byte [repeated]
    ResonateLv: byte
    ResonatePiece: byte [repeated]
    IsLock: byte
    IsLockSkill: byte [repeated]
    SupportSkills: {  [repeated]
      Index: number
      HeroCId: number
    }
    FameLv: word
    FameExp: number
  }

-- === s_campaign_select_buff ===
  Index: byte

-- === s_team_apply_join ===
  TeamUid: number

-- === c_equip_breakthrough ===
  EquipPos: byte
  Res: byte
  BreakLv: byte

-- === c_night_fight_hero_lineup ===
  HeroLineup: number [repeated]

-- === c_theater_chapterbonus ===
  chapterid: number
  starIdx: number

-- === s_league_tech_panel ===
  LeagueId: number
  WeekTechId: number

-- === s_campaign_trigger_on ===
  FieldId: number
  AreaId: number

-- === c_card_del ===
  Uid: number [repeated]

-- === s_battlefield_info ===
  Uid: number

-- === s_anti_addiction_report ===
  ruleName: string
  traceId: string
  execTime: number

-- === c_act_exchange_info ===
  ActId: number
  ExchangeTimes: {  [repeated]
    Id: number
    Num: number
    Unlock: byte
    UnlockNum: number
  }

-- === s_comment_comment ===
  Mod: string
  ModId: number
  Content: string

-- === c_league_buy_boss_challenge_times ===
  Times: number

-- === s_crosspvp_task_reward ===
  TaskId: number

-- === c_battlefield_info ===
  Uid: number
  CurFightGameId: number
  CurFightGameDone: number
  SeasonPoint: number
  HistoryList: {  [repeated]
    SeasonId: number
    Score: number
    Total: number
    Win: number
  }
  MatchFightData: season_info
  ScoreFightData: season_info
  HeroList: {  [repeated]
    Cid: number
    FightNum: number
    WinNum: number
  }
  HistoryHeroList: {  [repeated]
    Cid: number
    FightNum: number
    WinNum: number
  }
  PunishTime: number

-- === c_exchange_do ===
  Times: number
  Amount: number
  ItemId: number

-- === s_league_tech_tree_panel ===
  LeagueId: number

-- === c_relax_stage_boxinfo ===
  BoxInfo: {  [repeated]
    Uid: number
    BoxList: {  [repeated]
      ItemId: number
      Num: number
    }
    DailyBoxTimes: number
    TotalBoxTimes: number
    DailyRewardTimes: number
    TotalRewardTimes: number
  }

-- === c_act_jump_update_cond ===
  CondStatus: {  [repeated]
    Id: number
    Count: number
    Status: number
  }

-- === c_entrust_task_data ===
  EntrustTaskData: entrust_task_data

-- === s_group_team_swap_pos ===
  GroupId: number
  Pos1: byte
  Pos2: byte

-- === s_activity_shop_info ===
  ActType: number

-- === s_shop_refresh ===
  ShopId: number
  RefreshCount: number

-- === c_lottery_choose_up ===
  DrawId: number
  UpRatioId: number

-- === s_team_change_play ===
  PlayId: number
  Extra: number [repeated]

-- === c_equip_attr ===
  EquipAttrList: equip_attr_info

-- === s_card_lock_skill ===
  HeroCId: number
  Index: byte
  IsLock: byte

-- === s_pvp_user_load_ready ===
  UserUid: number

-- === s_equip_material_merge_to ===
  FromItemId: number
  ToItemId: number
  Count: number

-- === c_area_event_fight_times_status ===
  StageFightTimes: area_event_stage_times

-- === s_night_fight_enter_stage ===
  StageId: number
  Lineup: number [repeated]

-- === c_league_pvp_hero_update ===
  HeroList: league_pvp_hero_data [repeated]

-- === s_peak_battle_primary_seat_info ===
  SeatIndex: number

-- === c_sugar_room_exchange_count ===
  ExchangeCount: {  [repeated]
    Index: number
    Count: number
  }

-- === c_theater_enter ===
  ChapterInfo: {  [repeated]
    Id: number
    Status: number
  }
  StageInfo: {  [repeated]
    Id: number
    Status: number
    StarList: number [repeated]
    FullStarTime: number
  }

-- === s_home_change_name ===
  Floor: number
  Name: string

-- === c_shop_sell_equip ===
  ItemList: {  [repeated]
    ItemId: number
    Amount: number
  }

-- === c_group_finish_loading ===
  Uid: number

-- === c_offlinepvp_task ===
  TaskList: {  [repeated]
    Id: number
    Status: byte
    Val: number
  }

-- === s_home_leave ===

-- === c_lantern_start ===
  GqId: number

-- === c_group_cd_time ===
  Time: number

-- === s_battlefield_solo_enter ===
  Id: number
  MercenaryIdList: number [repeated]

-- === s_equip_upstar ===
  EquipPos: byte
  StarLv: byte

-- === c_stage_end_gm ===
  Result: number

-- === s_secret_refuse_key ===
  UserUid: number

-- === c_rogue_endless_end ===
  phase: number
  ScoreDetail: number [repeated]
  Time: number
  GlobalCoin: number

-- === c_group_team_change_hero ===
  GroupId: number
  Uid: number
  HeroUse: number

-- === s_hero_rank_star_get ===
  Id: number

-- === c_interaction_do ===
  Type: byte
  Index: number
  Uid: number
  Result: byte

-- === c_league_pvp_cd_list ===
  FightCDList: league_pvp_cd_data [repeated]

-- === c_act_exlottery_info ===
  ActId: number
  GuaranteeInfo: {  [repeated]
    GuaranteeId: number
    DrawNum: number
  }

-- === s_act_allsvr_stage_enter ===
  ActId: number
  LevelId: number
  Cid: number

-- === s_battlefield_task_finish ===
  Index: byte

-- === s_userinfo_sign ===
  Str: string

-- === c_group_map_list ===
  AreaId: number
  MapList: group_map_data [repeated]

-- === c_team_sync_info ===
  Uid: number
  type: number
  NumInfo: number [repeated]
  StrInfo: string [repeated]

-- === s_evaluate ===

-- === c_team_ready ===
  Uid: number
  IsReady: number

-- === c_stage_achievement_finish ===
  IdList: number [repeated]

-- === s_comment_reply_list ===
  Mod: string
  ModId: number
  SendUid: number
  ModIdIdx: number
  Page: number

-- === s_usj_task_reward ===
  TaskId: number

-- === s_funcopen_query ===
  TargetUid: number
  OpenId: byte

-- === c_grid_box_lottery ===
  ActId: number
  LotteryType: byte
  GainList: number [repeated]

-- === s_team_change_leader ===
  TargetUid: number

-- === s_offlinepvp_wipe ===
  OldRankId: number

-- === c_flipcard_update_count ===
  CurCount: number
  UseCount: number

-- === c_custom_gift_info ===
  GiftList: custom_gift [repeated]

-- === c_offlinepvp_rank_reward ===
  OldRankId: number
  NewRankId: number
  Reward: stage_reward [repeated]

-- === c_league_get_team_reward ===
  RewardId: number

-- === c_rogue_review ===
  Type: number
  HeroIndex: number
  List: {  [repeated]
    IsSucess: number
    BuffList: number [repeated]
    Score: number
    Rounds: number
  }

-- === c_world_task_pick_prestige ===
  IsSuccess: number
  FixedReward: stage_reward [repeated]
  RandomReward: stage_reward [repeated]
  RandomItem: number

-- === s_team_ask_for_leader ===

-- === c_scene_action_change ===
  Uid: number
  ActionId: number

-- === s_stage_activity_reward ===
  Id: number

-- === s_attached_card_lv ===
  TargetUid: number
  ItemList: item_data [repeated]
  Exp: number
  Lv: dword

-- === s_campaign_trigger_see ===
  FieldId: number
  AreaId: number

-- === s_league_pvp_view_member_records ===
  IsRival: number

-- === c_battlefield_rank_info ===
  States: byte [repeated]

-- === s_frame_robot ===
  Uid: number
  RobotUid: number
  CmdKey: number
  CmdData: number [repeated]

-- === s_campaign_enter ===
  CampaignId: number

-- === s_userinfo_base ===
  Uid: number [repeated]

-- === s_pressure_like ===
  Uid: number

-- === s_group_team_apply_clear ===
  GroupId: number

-- === c_group_team_all_info ===
  GroupId: number
  WanFaId: number
  ShowStatus: byte
  GroupDesc: string
  LeaderUid: number
  MemberList: group_member_info [repeated]
  Embattle: number [repeated]
  IntExtra: number [repeated]
  StrExtra: string [repeated]

-- === c_welfare_info ===
  Exchange: number
  FixDay: byte
  SignList: byte [repeated]
  TotalLogin: number [repeated]
  Strength: number [repeated]
  LevelRewards: number [repeated]

-- === c_secret_area_stage_fail ===
  Members: {  [repeated]
    UserUid: number
    HurtSum: number
    Reborn: number
  }
  KeyId: number

-- === c_group_team_new_setting ===
  GroupId: number
  ShowStatus: byte
  GroupDesc: string
  Difficult: number
  FightLimit: number

-- === c_card_take_bio_reward ===
  CardUid: number
  BiographyId: number
  IsSucc: byte

-- === s_platform_access_friend_share_total_reward ===
  RewardId: number

-- === c_rogue_event_choose ===
  TalkId: number
  CurHp: number

-- === s_lottery_draw ===
  DrawId: number
  Times: number
  ClientConsumeItemCount: number

-- === s_peak_battle_primary_occupy_seat ===
  SeatId: number
  SeatStatus: byte

-- === s_danmu_get_list ===
  Type: byte
  PlotID: number

-- === c_battlefield_pk_invite_ret ===
  Time: number

-- === c_item_special_reward ===
  ItemId: number
  RewardList: stage_reward [repeated]

-- === c_league_board_list ===
  LeagueId: number
  TopId: number
  BoardCount: number
  Pages: {  [repeated]
    PageNum: number
    BoardList: {  [repeated]
      BoardId: number
      Msg: string
      SupportCount: number
      OpposeCount: number
      CommentCount: number
      PublicTime: number
      IsSupport: byte
      IsOppose: byte
      MyCommentCount: number
      IsHot: byte
      SenderInfo: {
        Uid: number
        Name: string
        AvatarId: byte
        AvatarFrameId: byte
      }
    }
  }

-- === c_act_daily_stage_info ===
  ActId: number
  Count: {  [repeated]
    Id: number
    Count: number
    Extra: {
      NumList: number [repeated]
      StrList: string [repeated]
    }
  }

-- === s_scene_enter_end ===
  SceneId: number

-- === c_act_eye_sight_info ===
  List: {  [repeated]
    Id: byte
    State: byte
  }
  Record: number

-- === c_group_team_apply_list ===
  GroupId: number
  ApplyList: group_member_base_info [repeated]

-- === s_avatar_frame_use ===
  Id: number

-- === s_training_hero_info ===
  HeroId: number

-- === s_item_use ===
  ItemUid: number
  ItemId: number
  Amount: number
  NowAmount: number

-- === c_secret_area_drop_card ===
  UserUid: number
  CardPos: number

-- === c_rogue_benefit_choose ===
  ChooseType: number
  BuffList: number [repeated]

-- === s_offlinepvp_array ===
  AtkPos: offlinepvp_hero_pos [repeated]
  DefPos: offlinepvp_hero_pos [repeated]

-- === c_anti_addiction_execute ===
  List: {  [repeated]
    type: byte
    title: string
    msg: string
    url: string
    modal: byte
    data: string
    ratio: number
    ruleName: string
    traceId: string
  }

-- === s_act_return_unlock ===
  BounsId: number

-- === c_userinfo_dynamic ===
  Type: byte
  Param: number [repeated]

-- === c_stage_enter ===
  StageId: number
  StageUid: number
  Level: number
  Time: number
  Drama: number
  IsReconnect: byte
  NeedLagLog: byte
  IsRecord: byte
  Extra: {  [repeated]
    Key: number
    Value: number [repeated]
  }

-- === c_income_buff_update ===
  List: {  [repeated]
    Id: number
    EndTime: number
    Del: byte
  }

-- === c_collect_update ===
  List: {  [repeated]
    Type: byte
    Id: number
    Value: number
    State: byte
  }

-- === c_scene_bridge_hero_change ===
  Uid: number
  ShowHeroId: number
  ShapeCacheId: number

-- === s_client_stat ===
  StatId: byte
  NumData: number [repeated]
  StrData: string [repeated]

-- === s_act_ach_reward ===
  ActId: number
  RewardId: number

-- === c_friend_quick_send_strength ===
  TargetUids: number [repeated]

-- === c_userinfo_all_dynamic ===
  List: {  [repeated]
    Type: byte
    Param: number [repeated]
  }

-- === s_grid_box_choose ===
  ActId: number
  ChooseList: number [repeated]

-- === c_card_grow ===
  CardUid: number
  IsSuccess: number

-- === c_league_leave ===
  LeagueId: number
  ReasonId: byte

-- === s_teach_pvp_enter ===
  HeroCId: number [repeated]
  StageId: number
  RobotId: number

-- === s_area_event_switch_hero ===
  HeroUId: number

-- === c_card_show_info ===
  ActiveAttachedCardIdList: number [repeated]

-- === c_equip_dieset_break ===
  EquipPos: byte
  DiesetLv: byte

-- === s_equip_enhance ===
  EquipPos: byte
  EnhanceLv: number

-- === c_area_event_sync_status ===
  StageId: number
  EventRound: number
  ControlId: number
  TriggerOnMap: number [repeated]
  BoxRewardList: {  [repeated]
    ItemId: number
    Count: number
  }
  HeroInfo: area_event_hero_info [repeated]

-- === c_peak_battle_group_phase ===
  Phase: number
  PhaseTime: number

-- === c_group_team_admin_info ===
  TeamList: group_member_data [repeated]

-- === c_battlefield_pk_prepare ===
  Time: number

-- === s_team_match_cancel ===

-- === c_battlefield_task_remove ===
  Index: byte

-- === c_egg_info ===
  ETasks: egginfo [repeated]
  FinishTasks: number [repeated]

-- === s_league_tech_event_info ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte

-- === c_act_consume_update ===
  ActId: number
  Id: number [repeated]
  RewardList: stage_reward [repeated]

-- === c_home_interact_info ===
  ILike: home_liker [repeated]
  LikeMe: home_liker [repeated]
  Friend: {  [repeated]
    Uid: number
    Liker: dword
  }

-- === c_act_hero_rank ===
  CurPage: number
  TotalPage: number
  Page: top_rank_data [repeated]
  SelfRankInfo: top_rank_data

-- === c_night_fight_cache_stage_id ===
  CacheStageId: number

-- === s_toplist_one ===
  List: {  [repeated]
    ID: byte
    SubName: number
    RankUid: number
    IsCross: number
  }

-- === c_close_connection ===
  info: string

-- === c_activity_login_push ===
  Data: number [repeated]

-- === s_league_pvp_self_hero_list ===
  Uid: number

-- === c_shot_get_reward ===

-- === c_team_commend ===
  PlayId: number
  CommendList: team_commend_info [repeated]
  CommendType: number

-- === s_rogue_review ===
  Type: number
  HeroIndex: number

-- === s_replay_check ===

-- === c_async_cfg_update ===
  IdList: number [repeated]

-- === s_act_exlottery_info ===
  ActId: number

-- === s_crosspvp_buy ===
  Times: word
  Count: dword

-- === s_act_team_finish_task ===
  Id: byte

-- === s_night_fight_leave_stage ===
  LeaveType: number

-- === c_league_board_mine ===
  LeagueId: number
  BoardList: {  [repeated]
    BoardId: number
    Msg: string
    SupportCount: number
    OpposeCount: number
    CommentCount: number
    PublicTime: number
    IsSupport: byte
    IsOppose: byte
    IsHot: byte
  }

-- === s_offlinepvp_ready ===
  RankId: number

-- === c_card_breakup ===
  Uid: number [repeated]
  Reward: item_data [repeated]

-- === s_team_match ===
  MatchVal: number [repeated]

-- === s_group_finish_loading ===

-- === c_friend_recive_strength ===
  TargetUid: number

-- === s_danmu_praise ===
  Type: number
  ID: number
  BarrageID: number

-- === c_card_fetters_info ===
  FettersInfo: {  [repeated]
    Id: number
    Lv: number
    ExLv: number
    Fighting: number
  }

-- === c_home_furniture_produce ===
  Data: furniture_produce

-- === c_league_tech_buy ===
  LeagueId: number
  Id: number

-- === s_gem_list ===
  HeroCId: number [repeated]

-- === c_gm_result ===
  msg: string

-- === s_card_grow ===
  CardUid: number

-- === c_team_sync_quick_chat ===
  Msg: string [repeated]

-- === s_master_shop_goods_list ===
  ShopType: number

-- === s_league_pvp_leave_occupy ===

-- === s_business_extend_shop ===
  businessId: number

-- === s_crosspvp_match ===

-- === c_pressure_last_cycle ===
  Type: number
  CurCycle: byte
  Cycle: byte
  Score: number
  Rank: number
  Total: number

-- === c_reddot_info ===
  RedDot: {  [repeated]
    Id: number
    RedNum: number
  }

-- === c_business_extend_get_reward ===
  day: number
  index: number

-- === s_egg_sync ===
  EType: number
  CondType: string
  ParamList: number [repeated]

-- === s_offlinepvp_pro_reward ===

-- === s_crosspvp_hot ===

-- === s_home_enter ===
  OwnerUid: number

-- === s_attached_card_directional_compose ===
  ACardUids: number [repeated]

-- === c_group_team_go ===
  GroupId: number

-- === c_training_finish ===
  HeroCId: number
  SkillId: number

-- === s_group_team_league_list ===
  GroupId: number

-- === c_crosspvp_task ===
  IsUpdate: byte
  Tasks: {  [repeated]
    Id: number
    Status: byte
    Val: number
  }

-- === s_toplist_first ===
  List: {  [repeated]
    ID: byte
    SubName: number
    IsCross: number
  }

-- === c_shot_finish ===
  Point: number

-- === c_rogue_pass_start ===
  PassId: number

-- === c_friend_list ===
  Type: number
  UidList: number [repeated]

-- === s_hero_rank_task_finish ===
  Id: number

-- === s_league_change_name ===
  LeagueId: number
  Name: string

-- === s_pressure_stage_enter ===
  StageId: number

-- === c_crosspvp_task_reward ===
  TaskId: number

-- === s_team_deal_apply ===
  TargetUid: number
  Decision: number

-- === s_entrust_task_start ===
  TaskUniqId: number
  CardUidList: number [repeated]

-- === c_group_scene_exit ===

-- === c_battlefield_pk_refuse ===
  MsgId: number

-- === s_act_daily_stage_report ===
  ActId: number
  Result: byte
  Count: number

-- === s_league_join_boss ===
  LeagueId: number
  HeroUid: number

-- === c_act_team_invite ===
  InviteList: {  [repeated]
    Uid: number
    Name: string
    Level: byte
    TopLevel: number
    Avatar: number
    AvatarFrame: number
  }

-- === c_stage_loss ===

-- === s_league_ad_panel ===
  LeagueId: number

-- === c_new_connect ===
  GsId: number
  Addr: string
  TcpPort: number
  UdpPort: number
  VerifyStr: string

-- === c_league_pvp_view_panel ===
  SelfPvpScore: number
  SelfCamp: number
  RivalCamp: number
  RivalLeagueId: number
  RivalLeagueName: string
  RivalLeagueIcon: number
  RivalLeagueFrameIcon: number
  RivalLeaguePvpScore: number

-- === s_league_tech_event_deal ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte

-- === c_danmu_praise ===
  Type: number
  ID: number
  BarrageID: number

-- === c_act_seven_day_info ===
  ActId: number
  Buys: {  [repeated]
    GoodsId: number
    Buys: number
  }

-- === c_battlefield_stmatch ===
  result: number

-- === c_send_pvp_report ===
  Type: byte
  IsWin: byte
  WinUid: number
  WinInfo: pvp_report
  LoseInfo: pvp_report

-- === s_pvp_quit ===
  UserUid: number

-- === c_peak_battle_bet_info ===
  BetsInfo: {  [repeated]
    TeamId: number
    SupportUid: number
    UserList: peak_battle_data [repeated]
  }

-- === c_scene_shape_cachedata ===
  ShapeCacheId: number
  Shape: number
  Attach: npair_number [repeated]

-- === s_time_ping ===
  SendTime: number

-- === s_peak_battle_support ===
  Uid: number
  SupportId: number

-- === c_usj_update_zone_reward ===
  RewardType: number
  ZoneId: number
  RewardState: number

-- === c_lottery_load ===
  DrawInfo: {  [repeated]
    DrawId: number
    HaveDraw: byte
    LastFreeTime: number
    UpRatioId: number
  }
  GuaranteesInfo: {  [repeated]
    GuaranteesType: number
    ProcessInfo: {  [repeated]
      ImportantId: number
      AccumulationTimes: number
    }
  }

-- === c_peak_battle_open_time ===
  OpenTime: number
  ActSwitch: byte

-- === c_act_boss_challenge_over ===
  JoinTimes: number
  Damage: number
  TotalDamage: number
  Point: number
  TotalPoint: number

-- === c_item_special_item ===
  item: special_item_info

-- === c_team_join ===
  MeamInfo: team_member_info

-- === c_league_pvp_view_declaration ===
  Declaration: string

-- === c_training_get_reward ===
  HeroCId: number
  SkillId: number

-- === s_world_task_ignore_auto_finish_tips ===
  Flag: byte

-- === s_rune_enchance ===
  Uid: number
  FeedUids: number [repeated]
  FeedIds: {  [repeated]
    ItemId: number
    Num: number
  }

-- === s_sugar_room_exchange ===
  ExchangeIndex: number
  ExchangeCount: number

-- === s_lottery_load ===

-- === c_scene_block_change ===
  TopX: number
  TopZ: number
  BottomX: number
  BottomZ: number
  Block: number
  Invert: byte

-- === s_team_play_start ===
  PlayId: number
  Extra: number [repeated]

-- === s_friend_choose ===

-- === s_league_pvp_total_score ===

-- === c_campaign_task_add ===
  TaskInfo: campaign_task_info

-- === s_login_player_add ===
  TypeId: number

-- === c_team_apply_join ===
  IsSucc: number

-- === s_league_board_comment_list ===
  LeagueId: number
  BoardId: number

-- === c_league_tech_panel ===
  LeagueId: number
  WeekTechId: number
  JoinCount: byte
  Progress: number
  Time: number
  MemberList: {  [repeated]
    MemberUid: number
    MemberName: string
    HeroClass: number
    Sign: string
    JoinNo: byte
  }

-- === c_league_pvp_be_kill ===
  Declaration: string
  UserInfo: league_pvp_fight_data

-- === c_exchange_info ===
  info: {  [repeated]
    ItemId: number
    Times: number
    LastTime: number
  }

-- === c_league_member_list ===
  LeagueId: number
  MemberInfo: {  [repeated]
    Uid: number
    Name: string
    HeadIcon: number
    HeadFrameIcon: number
    Job: byte
    Lv: byte
    TopLv: number
    Achieve: number
    Online: byte
    LogoutTime: dword
    WeekGongXun: number
    ActiveStar: byte
    JoinWeekTechId: number
    JoinNo: byte
  }

-- === s_pvp_end ===
  UserUid: number

-- === c_league_pvp_con_kill ===
  ConKill: number
  UserPvpList: league_pvp_fight_data [repeated]

-- === c_emergency_info ===
  Events: emergency_event [repeated]
  Chance: number
  SupportTime: number

-- === c_frame_obj_report_local ===
  DataIndex: number

-- === c_hero_rank_status_update ===
  AttrList: {  [repeated]
    Id: string
    Value: number
  }
  BuffList: number

-- === c_skill_spec_level_list ===
  SpecInfoList: spec_level_info [repeated]

-- === c_stage_all_finish_loading ===

-- === c_home_furniture_uid ===
  IdMap: {  [repeated]
    Tid: string
    Uid: number
  }

-- === c_reconnect_frame ===
  LastFrame: number
  FrameData: {  [repeated]
    FrameId: number
    Data: {  [repeated]
      Cmd: number [repeated]
    }
  }
  Index: byte

-- === s_platform_access_friend_share_daily_reward ===

-- === s_all_server_cond_get_reward ===
  Id: number

-- === c_act_allsvr_stage_reward ===
  ActId: number
  AllSvrScore: number
  AllSvrCond: {  [repeated]
    Id: number
    State: byte
  }

-- === c_welfare_total_login ===
  Id: number
  TotalLogin: number [repeated]

-- === s_league_about ===
  LeagueId: number

-- === c_league_pvp_total_score ===
  TotalScore: number

-- === s_shop_info ===
  shopIds: number [repeated]

-- === s_shop_buy ===
  ShopId: number
  GoodsId: number
  Amount: number
  TotalPrice: number
  CurrencyAmount: number

-- === c_act_baohao_practice_new_task ===
  Pos: number
  TaskID: number
  CompCount: number
  Desc: string
  Goto: number
  Goto2: number
  Points: number
  Title: string
  Type: string
  Rewards: {  [repeated]
  }
  Count: number
  Status: number

-- === s_league_change_icon ===
  LeagueId: number
  IconType: number
  Icon: number

-- === s_league_tech_modify_shop_manager_sign ===
  LeagueId: number
  ManagerSign: string

-- === c_relax_stage_fail ===
  Members: {  [repeated]
    Uid: number
    Dps: number
    Reborn: number
  }

-- === c_card_go_to_bridge_fight ===
  HeroUid: number

-- === c_platform_access_friend_share_panel ===
  DailyRewardStatus: byte
  TotalShareDays: word
  RewardList: number [repeated]

-- === c_crosspvp_ace ===
  AceInfo: {  [repeated]
    Season: number
    STime: number
    ETime: number
    AceList: {  [repeated]
      Uid: number
      Point: number
      Rank: number
      HostId: number
      Name: string
      Faceicon: number
      Faceframe: number
      Level: number
      TopLevel: number
      Tbpos: crosspvp_pos [repeated]
      RankId: word
    }
  }

-- === s_team_change_hero ===
  HeroId: number

-- === s_friend_del_soon_chat ===
  TargetUid: number

-- === c_act_secret_record_list ===
  ActId: number
  RecordList: {  [repeated]
    NameList: string [repeated]
    StageGroupId: number
    Floor: word
    Score: number
    Time: dword
    StageLevel: byte
  }

-- === s_home_update_produce ===
  FurnitureUid: number

-- === c_home_floor_furniture_update ===
  Data: home_floor_furniture

-- === c_friend_del_soon_chat ===
  TargetUid: number

-- === s_league_apply_done ===
  LeagueId: number
  TargetUid: number
  Result: byte

-- === c_stage_report ===

-- === c_stage_show_reward ===
  RewardList: stage_reward [repeated]

-- === c_league_pvp_view_pvp_records ===
  IsRival: number
  LeaguePvpRecords: league_pvp_record [repeated]

-- === c_league_pvp_cd_change ===
  FightCDList: league_pvp_cd_data [repeated]

-- === s_crosspvp_task ===

-- === c_master_shop_goods_list ===
  ShopType: number
  GoodsList: {  [repeated]
    GoodsUid: number
    RemainAmount: number
    HadAmount: number
  }

-- === c_frame_correct ===
  CFrame: number
  AtrType: byte [repeated]

-- === c_area_event_stage_pass ===
  Star: number [repeated]
  FirstPass: number
  FirstPassPrize: stage_reward [repeated]
  ImportantPrize: stage_reward [repeated]

-- === s_act_pickbox_pick ===
  PoolId: number
  Count: number

-- === s_frame_obj_report ===
  Uid: number
  CFrame: number
  AtrType: byte
  Data: {  [repeated]
    id: number
    value: number
    extval: number
    extdata: number [repeated]
  }

-- === c_funcopen_info ===
  id: byte
  status: byte

-- === c_danmu_update ===
  Type: number
  ID: number
  Msg: string
  Postion: byte
  Color: byte
  BarrageID: number

-- === c_friend_sync_int ===
  SyncInt: {  [repeated]
    key: byte
    value: number
  }

-- === c_league_tech_shop_panel ===
  WeekNo: number
  DayNo: number
  LeagueId: number
  ManagerUid: number
  ManagerName: string
  ManagerHeroClass: number
  ManagerSign: string
  DiscountGoodsList: number [repeated]
  BuyList: {  [repeated]
    GoodsId: number
    BuyCount: byte
  }
  SessionId: dword

-- === s_act_team_clear_invite ===

-- === c_data_str ===
  PtoName: string
  CurPage: byte
  MaxPage: byte
  PtoData: string

-- === c_secret_area_history_add ===
  History: secret_area_history

-- === c_rogue_save ===
  Index: number
  HeroIndex: number
  Name: string
  BuffList: number [repeated]

-- === c_group_boss_data ===
  Index: number
  BossHp: number
  Shield: number

-- === s_team_del_robot ===
  Index: number

-- === s_pressure_info ===

-- === c_peak_battle_group_ready ===
  MyReady: byte
  RivalReady: byte

-- === c_daily_recharge_info ===
  Total: number
  List: {  [repeated]
    SubId: number
    Day: byte
    State: byte [repeated]
  }

-- === c_league_tech_update_progress ===
  LeagueId: number
  WeekTechId: number
  JoinCount: byte
  Progress: number
  Time: number
  ProgressInfo: {  [repeated]
    Percent: byte
    Time: dword
  }

-- === c_team_del_robot ===
  Index: number

-- === c_group_team_list ===
  GroupList: {  [repeated]
    GroupId: number
    ChannelId: number
    ShowStatus: byte
    GroupDesc: string
    LeaderUid: number
    MemberList: number [repeated]
    Status: byte
    ApplyStatus: byte
    WanFaId: number
    IntExtra: number [repeated]
    StrExtra: string [repeated]
  }

-- === c_group_team_apply ===
  GroupId: number

-- === s_group_scene_exit ===

-- === s_league_boss_rank ===
  LeagueId: number
  RealDayNo: number
  Version: number

-- === c_pressure_hero_fight ===
  HeroUid: number

-- === c_area_event_hero_list ===
  Type: number
  NormalLineup: number [repeated]
  ActLineup: number [repeated]

-- === c_scene_enter_end ===

-- === s_comment_delreply ===
  Mod: string
  ModId: number
  SenderUid: number
  ModIdIdx: number
  ReplyIdx: number
  ReplyUid: number

-- === c_set_ctrl ===
  IsCtrl: byte
  RoleUid: number

-- === s_league_get_rank_info ===
  LeagueId: number

-- === s_act_hero_bp_exchange ===
  ActId: number
  Num: number

-- === s_mail_get_info ===
  iMailId: number

-- === s_campaign_data_list ===

-- === c_userinfo_badge_get ===
  List: {  [repeated]
    Id: number
    Value: number
    State: byte
    Time: number
  }

-- === c_rogue_buy ===
  Index: number
  Type: number
  InnerCoin: number

-- === s_group_team_modify_setting ===
  GroupId: number
  ShowStatus: byte
  GroupDesc: string
  Difficult: number
  FightLimit: number

-- === c_sys_message ===
  msg: string
  type: byte

-- === s_admission_manual_get_reward ===
  Id: word

-- === c_pvp_start_fighting ===

-- === c_async_cfg_one ===
  AsyncId: byte
  Key: number
  PackCfg: string

-- === c_crosspvp_rank_info ===
  RankIds: number [repeated]

-- === s_all_server_cond_get_info ===
  Type: byte

-- === s_campaign_task_submit ===
  Id: number

-- === s_reconnect_frame ===
  Uid: number
  CFrame: number

-- === c_act_return_check_goods ===
  Id: number
  Result: byte

-- === c_grid_box_info ===
  ActId: number
  IsChoose: byte
  ResetTimes: number
  ItemList: number [repeated]
  ChooseList: number [repeated]
  GainList: number [repeated]

-- === s_home_get_furniture_produce ===
  FurnitureUid: number

-- === c_act_rescue_info ===
  StageList: {  [repeated]
    Id: byte
    Point: number
    State: number
  }

-- === s_zhanling_info ===

-- === c_flipcard_update_reward ===
  TotalReward: byte
  CycleReward: byte [repeated]

-- === s_emergency_choose_event ===
  EventUid: number

-- === s_peak_battle_pick_hero ===
  HeroCIdList: number [repeated]

-- === s_team_invite ===
  TargetUid: number
  CommendType: byte

-- === c_group_team_change_leader ===
  GroupId: number
  NewLeaderUid: number

-- === c_task_req_enter_stage ===
  AskType: number
  TagErrTaskId: number

-- === c_crosspvp_top_list ===
  Season: number
  PageNums: number [repeated]
  MaxPageNum: number
  SelfUid: number
  Pages: {  [repeated]
    PageNum: number
    Page: {  [repeated]
      Rank: number
      Uid: number
      Name: string
      AvatarId: dword
      AvatarFrameId: dword
      Fighting: number
      Point: number
      Level: dword
      TopLevel: dword
      RankId: number
      HostId: number
      CWin: dword
      CFight: dword
    }
  }
  selfInfo: {
    Rank: number
    Uid: number
    Name: string
    AvatarId: dword
    AvatarFrameId: dword
    Fighting: number
    Point: number
    Level: dword
    TopLevel: dword
    RankId: number
    HostId: number
    CWin: dword
    CFight: dword
  }

-- === c_league_donate ===
  LeagueId: number
  DonateTimes: byte
  LeagueDonateTimes: word
  Exp: number
  Money: number
  WeekGongXun: number
  LeagueMoneyLogNo: number
  LeagueMoneyLogs: {  [repeated]
    iMoneyLogId: number
    arrArgs: string [repeated]
    iMoneyLogTime: number
    iMoneyLogNo: number
  }
  LeagueDonateLogNo: number
  LeagueDonateLogs: {  [repeated]
    iDonateLogId: number
    arrArgs: string [repeated]
    iDonateLogTime: number
    iDonateLogNo: number
  }

-- === c_friend_add ===
  Type: number
  Info: friendinfo

-- === s_rune_oper ===
  Uid: number
  Type: number
  MId: number
  Index: byte

-- === c_league_tech_fight_event_info ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte
  EventProgress: number
  EventDamageList: {  [repeated]
    MemberUid: number
    MemberName: string
    Damage: number
  }
  DealTimes: byte

-- === c_league_modify_ad ===
  LeagueId: number
  Ad: string

-- === s_crosspvp_fight ===

-- === s_scene_move ===
  Path: {  [repeated]
    X: number
    Y: number
    Z: number
    Face: number
    Speed: number
    ChState: number
    ChAction: byte
    Extra: number
  }

-- === c_fenshen_daily_reward ===
  DailyRewardStatus: byte

-- === s_league_start_boss ===
  LeagueId: number

-- === s_act_secret_record_list ===
  ActId: number

-- === c_all_server_cond_update ===
  IdList: number [repeated]

-- === c_league_tech_event_finish_reward ===
  LeagueId: number
  WeekTechId: number
  EventIdx: byte [repeated]

-- === c_rogue_pass_hero ===
  GroupId: number
  HeroIndex: number

-- === c_campaign_property_del ===
  CampaignId: number
  Property: {  [repeated]
    PropertyId: number
    Count: number
  }

-- === c_league_log ===
  LeagueId: number
  LeagueLogNo: number
  LeagueLogs: {  [repeated]
    iLogId: number
    arrArgs: string [repeated]
    iLogTime: number
    iLogNo: number
  }

-- === c_chaos_choose_end ===
  SelfHeros: {  [repeated]
    HeroId: number
    RobotId: number
    Level: number
    RankId: number
    Name: string
    AvatarId: number
    AvatarFrameId: number
  }
  OtherHeros: {  [repeated]
    HeroId: number
    RobotId: number
    Level: number
    RankId: number
    Name: string
    AvatarId: number
    AvatarFrameId: number
  }

-- === s_campaign_task_update ===
  Id: number
  Type: string
  ParamList: number [repeated]

-- === c_userinfo_brief ===
  List: {  [repeated]
    Uid: number
    Avatar: number
    AvatarFrame: number
    TeamUid: number
    SvrId: number
  }

-- === c_week_sign_get ===
  Type: byte

-- === s_chaos_season_info ===
  SeasonId: number

-- === s_share_make_up ===
  Id: number

-- === s_usj_have_show_end_reward ===

-- === c_home_role_interact ===
  RoleId: number

-- === c_group_team_invite_done ===
  GroupId: number

-- === s_attached_card_reform ===
  ACardUids: number
  Index: number
  FeedUids: number [repeated]

-- === s_fenshen_start_panel ===

-- === c_attached_card_reset ===
  TargetUid: number

-- === s_secret_insert_key ===
  KeyOwerUid: number
  KeyId: number

-- === c_campaign_data_list ===
  Data: {  [repeated]
    CampaignId: number
    Cache: byte
    FinishTrigger: {  [repeated]
      FieldId: number
      TriggerList: number [repeated]
    }
    FinishTask: number [repeated]
    EnterFlag: byte
  }

-- === c_group_goto_channel ===
  GroupId: number
  ChannelId: number

-- === c_chat_frame_unlock ===
  List: {  [repeated]
    Id: number
    Value: number
    State: byte
  }

-- === c_login_checkstr ===
  CheckStr: string

-- === c_fenshen_aid_panel ===
  TotalJoinDays: number
  TotalRightTimes: number
  AidRewardIdList: number [repeated]

-- === s_secret_out_key ===

-- === c_league_board_oper ===
  LeagueId: number
  BoardId: number
  OperType: byte
  SupportCount: number
  OpposeCount: number
  IsSupport: byte
  IsOppose: byte

-- === c_usj_update_hero ===
  HeroList: {  [repeated]
    HeroUid: number
    HpPercent: number
    DeathTime: number
  }

-- === c_act_list ===
  ActData: {  [repeated]
    ActId: number
    ActType: number
    StartTime: number
    EndTime: number
    SyncInfo: string
  }

-- === c_league_get_rank_info ===
  LeagueId: number
  RankInfo: {
    Lv: byte
    Ad: string
    MemberAmount: word
    LeaderName: string
  }

-- === c_top_broadcast_secret_rangeId ===
  GroupList: {  [repeated]
    GroupId: number
    LevelRangeId: number
  }

-- === c_league_kick ===
  LeagueId: number
  TargetUid: number
  MemberAmount: word
  OnlineMemberAmount: word

-- === c_act_get_reward ===
  ActId: number
  RewardId: number
  NumList: number [repeated]
  StrList: string [repeated]

-- === s_act_exchange ===
  ActId: number
  ExchangeId: number
  ExchangeItem: number
  CCostAmout: number
  ClientCostRemainCount: number

-- === s_rogue_endless_fight ===
  HeroIndex: number
  Index: number

-- === s_group_team_apply_done ===
  GroupId: number
  TargetUid: number
  Result: byte

-- === c_scene_block_change_list ===
  BlockList: {  [repeated]
    TopX: number
    TopZ: number
    BottomX: number
    BottomZ: number
    Block: number
    Invert: byte
  }

-- === c_act_boss_challenge_server_ach ===
  AchList: number [repeated]

-- === s_league_board_info ===
  LeagueId: number

-- === s_home_clean ===

-- === s_relax_stage_choose ===
  StageId: number

-- === s_league_apply ===
  LeagueId: number

-- === s_home_role_event_finish ===
  RoleId: number

-- === s_rogue_pass_info ===

-- === c_exchange_code ===
  code: number
  itemList: {  [repeated]
    ItemId: number
    count: number
    extra: string [repeated]
  }

-- === c_card_resonance ===
  Uid: number
  PieceId: number [repeated]
  RewardList: stage_reward [repeated]

-- === c_danmu_get_list ===
  barrageList: {  [repeated]
    Msg: string
    Postion: byte
    Color: byte
    PCount: number
    BParise: byte
    Icon: byte
    Uid: number
    BarrageID: number
  }

-- === s_hero_class_answer ===
  Idx: byte
  Answer: byte

-- === s_scene_player_info ===
  Uid: number

-- === c_danmu_change_icon ===
  Icon: number

-- === s_offlinepvp_rank_reward ===

-- === c_league_pvp_scene_info ===
  StartTime: number
  LeagueSceneData: league_pvp_scene_data [repeated]
  BattleLog: number [repeated]
  Reports: league_pvp_report [repeated]
  HeroList: league_pvp_hero_data [repeated]
  CdList: league_pvp_cd_data [repeated]

-- === c_feedback_message ===
  ID: number
  Msg: string [repeated]
  CallbackID: number

-- === c_usj_update_score_reward ===
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === s_pressure_message ===
  Message: string

-- === c_rogue_info ===
  GlobalCoin: number
  GlobalBuffIds: number [repeated]
  TodayGlobalCoin: number
  TotalGlobalCoin: number
  BenefitRecord: {  [repeated]
    BuffList: number [repeated]
    HeroIndex: number
    Index: number
    Name: string
  }
  CurSvrId: number

-- === c_home_role_event ===
  Data: home_role_event

-- === s_league_pvp_scene_info ===

-- === s_group_team_go ===
  GroupId: number

-- === c_campaign_select_buff_update ===
  SelectBuff: number [repeated]

-- === s_equip_unlock ===
  EquipUid: number

-- === s_act_monopoly_use_item ===
  ActId: number
  Id: number
  ItemNum: number
  Params: number [repeated]

-- === s_battlefield_get_rank_reward ===
  Id: byte

-- === s_offlinepvp_replace ===
  IsProMote: byte

-- === s_home_update_role_mood ===
  RoleId: number

-- === c_secret_area_clear_cycle_record ===

-- === c_emergency_add ===
  Events: emergency_event
  Chance: number

-- === c_campaign_buff_update ===
  CampaignId: number
  Buff: number [repeated]

-- === s_rogue_event_choose ===
  Index: number

-- === c_resource_stage_reward ===
  Reward: stage_reward [repeated]
  FirstPassReward: stage_reward [repeated]
  LeagueItems: stage_reward [repeated]

-- === s_share_info ===

-- === s_act_empty_shop_stage_enter ===
  StageIndex: number
  HeroUid: number

-- === s_offlinepvp_buy ===
  Times: number

-- === s_usj_cycle_id ===

-- === c_team_back_room ===

-- === c_rune_enchance ===
  Uid: number

-- === c_group_open_map ===
  MapAttackArea: {  [repeated]
    StageId: number
    TeamList: number [repeated]
    Tag: number
    IsDoor: number
  }

-- === c_pay_item ===
  ShopId: number
  GoodsId: number
  Token: string
  Url: string
  Extra: string [repeated]

-- === s_theater_chapterbonus ===
  chapterid: number
  starIdx: number

-- === c_userinfo_birthday_set ===
  HideBirthday: byte
  SetBirthdayTime: number
  Year: number
  Month: byte
  Day: byte

-- === s_scene_obj_curid ===
  CurId: number

-- === s_league_quick_apply_del ===
  LeagueId: number

-- === c_league_boss_rank ===
  RealDayNo: number
  Version: number
  MemberDamageList: {  [repeated]
    Uid: number
    Damage: number
    Time: dword
    Name: string
    HeadIcon: number
    HeadFrameIcon: number
  }

-- === s_group_captain_alter ===
  AreaId: number
  Index: number
  TeamId: number

-- === c_pvp_end ===
  PlayerUid: number
  MercenayrId: number
  IsPVPEnd: byte

-- === s_userinfo_brief ===
  Uid: number [repeated]

-- === s_league_pvp_apply ===

-- === s_team_search ===
  PlayId: number
  Extra: number [repeated]
  IsAuto: byte

-- === c_chaos_match_suc ===
  Info: {  [repeated]
    Uid: number
    IsMate: number
    RobotId: number
    Level: number
    RankId: number
    Name: string
    AvatarId: number
    AvatarFrameId: number
    HeroId: number
    MatchTime: number
    AlwaysHeroCId: number [repeated]
  }
  AlwaysHeroCId: number [repeated]

-- === c_equip_inherit ===
  ToEquipUid: number

-- === c_comment_like ===
  CommentId: number
  SenderUid: number
  CommentIdx: number
  CommentInfo: commentinfo

-- === c_debug_draw_pos ===
  Uid: number
  PosX: number
  PosY: number
  Dir: number

-- === s_userinfo_sex ===
  Sex: byte

-- === s_league_icon ===
  LeagueId: number

-- === s_mail_get_attach ===
  iMailId: number

-- === s_office_pick_step ===
  Index: number

-- === c_stage_is_back ===
  StageId: number

-- === c_league_pvp_result ===
  WinCamp: number
  LeagueResult: league_pvp_result [repeated]
  MvpData: league_pvp_mvp_data

-- === c_fenshen_aid_reward ===
  AidRewardId: number

-- === c_guide_finish ===
  Sets: number [repeated]
  Ids: number [repeated]

-- === s_chaos_record_detail ===
  RecordId: number

-- === s_skill_level_up ===
  HeroUid: number
  SkillId: number
  AutoLevelUp: byte

-- === c_pay_item_confirm ===
  ShopId: number
  GoodsId: number
  Token: string
  CheckType: number

-- === s_flipcard_get_count ===
  Id: number

-- === s_resource_stage_reenter ===
  Id: number
  HeroUid: number

-- === c_interaction_new_emoticon ===
  Type: byte
  EmoticonId: number

-- === s_userinfo_badge ===
  List: byte [repeated]

-- === c_battlefield_pk_quit_ret ===

-- === c_stage_offlinepvp_pos ===
  AtkPos: offlinepvp_hero_pos [repeated]
  DefPos: offlinepvp_hero_pos [repeated]
  AtkInfo: {
    Name: string
    Fighting: number
    RankId: number
    Level: word
    TopLevel: number
  }
  DefInfo: {
    Name: string
    Fighting: number
    RankId: number
    Level: word
    TopLevel: number
  }

-- === c_peak_battle_primary_shop_count ===
  ShopCount: number

-- === c_league_apply_del ===
  TargetUid: number [repeated]

-- === s_battlefield_cancel_match ===
  type: number

-- === c_achieve_getreward ===
  Id: number

-- === c_custom_gift_update ===
  Info: custom_gift

-- === c_card_attr_change ===
  Uid: number
  Uid: number
  AttrName: string [repeated]
  Value: number [repeated]

-- === c_scene_trigger_create ===
  AddList: {  [repeated]
    Uid: number
    Id: number
    AreaId: number
    X: number
    Y: number
    Face: number
    Width: number
    Height: number
    Args: string [repeated]
    State: byte
  }

-- === c_top_level_up ===
  OldLv: number
  Level: number

-- === s_league_pvp_report ===
  Uid: number
  TotalDamage: number

-- === s_attached_card_active_show ===
  AttachedCardId: number

-- === s_league_donate_panel ===
  LeagueId: number
  LeagueDonateLogNo: number

-- === c_league_pvp_week_join ===
  WeekJoin: number

-- === c_campaign_trigger_on ===
  FieldId: number
  AreaId: number

-- === s_tsssdk_anti ===
  Data: string

-- === c_battlefield_status ===
  begintime: number
  endtime: number

-- === c_peak_battle_primary_rival_info ===
  RivalInfo: {  [repeated]
    Uid: number
    Name: string
    FaceIcon: number
    FaceFrame: number
    HeroCId: number
    HeroId: number
    Fighting: number
    ShapeId: number
  }

-- === c_time_ping_change ===
  Uid: number
  PingTime: number

-- === c_teach_finish ===
  HeroCId: number
  SkillList: {  [repeated]
    SkillId: number
    Count: number
  }

-- === c_area_event_leave_stage ===
  LeaveType: number

-- === s_home_get_checkin_reward ===
  TaskId: number

-- === s_group_team_admin_info ===

-- === c_team_add_robot ===
  Robots: {  [repeated]
    Robot: robot_info
    Index: number
  }

-- === c_league_pvp_sec_update ===
  ResourceScores: {  [repeated]
    ResourceId: number
    Score: number
  }
  ResourceSpeeds: number [repeated]
  ResourcesTotal: number [repeated]

-- === s_task_lock_trigger ===
  task_id: number
  IsLock: number

-- === c_usj_task ===
  TaskList: {  [repeated]
    Id: number
    Status: byte
    CurValue: number
  }

-- === c_area_event_hero_info ===
  HeroInfo: area_event_hero_info [repeated]

-- === c_team_set ===
  Lv: number
  Message: string
  SearcLv: number
  TotalScore: number

-- === s_league_send_ad ===
  LeagueId: number
  Msg: string
  ExtData: string

-- === s_hero_rank_hero_star ===
  Cid: number

-- === s_welfare_info ===

-- === s_group_channel_list ===
  GroupId: number
  Page: word

-- === s_userinfo_tag ===
  Id: byte [repeated]

-- === s_usj_enter_next_zone ===

-- === s_act_exlottery_draw ===
  DrawId: number
  Times: byte
  ClientItemRemainCount: number

-- === s_scene_line_info ===
  SceneId: number

-- === s_achieve_overview ===

-- === c_league_list_info ===
  LeagueId: number
  LeagueListInfo: {
    LeaderUid: number
    Name: string
    LeaderName: string
    Ad: string
  }

-- === c_battlefield_rank_get ===
  Id: byte

-- === c_all_server_cond_get_reward ===
  Id: number
  Status: byte

-- === s_egg_info ===

-- === c_act_jump_set_score ===
  DailyStatus: number
  DailyMaxScore: number
  IsEgg: number
  RewardList: {  [repeated]
    ItemId: number
    count: number
  }

-- === c_peak_battle_top_four ===
  TopFourList: peak_rank_data [repeated]

-- === c_role_change_name ===
  Name: string

-- === c_interaction_config_add ===
  Type: byte
  EmoticonId: number
  Index: number
  HeroId: number
  Result: byte

-- === s_team_out_team ===

-- === c_area_event_stage_cache_id ===
  StageId: number

-- === c_group_team_modify_setting ===
  GroupId: number

-- === s_stage_bonus ===
  StageUid: number
  StageId: number
  Result: number
  StarList: number [repeated]
  TotalTime: number
  PuaseTime: number
  DramaFinish: number [repeated]

-- === s_skill_get_skill_level_list ===
  HeroUidList: number [repeated]

-- === c_league_pvp_mvp_member ===
  MvpMember: {
    LeagueId: number
    Uid: number
    Name: string
    Level: number
    FaceIcon: number
    FaceFrame: number
    HeroId: number
    ShapeId: number
    BattleLog: number [repeated]
    Damage: number
  }

-- === c_peak_battle_fight_log ===
  LogType: number
  Logs: {  [repeated]
    FightType: number
    Bit: byte
    WinUid: number
    Time: number
    PlayId: number
    LogData: peak_battle_log [repeated]
  }

-- === c_equip_upstar ===
  EquipPos: byte
  StarLv: byte

-- === s_card_go_to_bridge_fight ===
  HeroUid: number

-- === s_attached_card_active_book ===
  ItemId: number

-- === c_battlefield_receive_player_info ===
  PlayerUid: number
  CurScore: number
  PlayerName: string
  MercenaryUidList: number [repeated]
  IsReconnect: byte

-- === s_stage_extra_reward ===

-- === s_get_sync_attr ===
  Uid: number

-- === s_league_leave ===
  LeagueId: number

-- === c_city_level_info ===
  Level: word
  ClickList: word [repeated]

-- === s_card_chip_to_hero ===
  HeroClassId: number

-- === s_fashion_info ===

-- === c_battlefield_pk_other_cancel_invite ===
  Uid: number

-- === c_item_send_use_count ===
  DayUseCount: {  [repeated]
    ItemId: number
    DayUseCount: byte
  }
  WeekUseCount: {  [repeated]
    ItemId: number
    WeekUseCount: byte
  }

-- === s_friend_send_strength ===
  Uid: number

-- === s_home_interact_info ===

-- === c_gem_del ===
  UUid: number [repeated]

-- === c_equip_material_merge_auto ===
  ItemId: number

-- === c_skill_get_spec_level ===
  SpecInfo: spec_level_info

-- === c_scene_npc_create ===
  NpcList: {  [repeated]
    Uid: number
    Id: number
    X: number
    Y: number
    Z: number
    Face: number
    Version: number
    ShapeId: number
    Attach: npair_number [repeated]
    HideStatus: number
    AreaId: number
    StartAnim: string
    BTName: string
    ForceShow: byte
  }

-- === c_team_new_apply_join ===
  Apply: team_apply_info [repeated]

-- === c_user_create ===
  user: user
  shape: number
  attach: npair_number [repeated]
  shape_cache_id: number
  version: number
  operator: byte
  ShowShapeId: number
  ShowShapeCacheId: number

-- === s_common_procotol ===
  Action: number
  JsonArgs: string

-- === s_world_task_auto_finish ===
  TaskId: number

-- === c_team_change_play ===
  PlayId: number
  Extra: {  [repeated]
    Key: string
    Val: number
  }

-- === c_league_apply_done ===
  LeagueId: number
  MemberAmount: word
  OnlineMemberAmount: word

-- === s_frame_ping ===
  Uid: number
  CFrame: number
  SendTime: number

-- === s_client_stat_frame ===
  uid: number
  iStageId: number
  iFrame: number
  iImageLevel: byte

-- === s_area_event_fight_over ===
  StageId: number
  IsWin: number
  UseTime: number

-- === s_group_team_ready ===
  GroupId: number
  Result: byte

-- === c_act_user_info ===
  ActId: number
  NumList: number [repeated]
  StrList: string [repeated]

-- === c_attached_card_active_show ===
  AttachedCardId: number

-- === c_act_baohao_practice_update_task ===
  CurPoints: number
  ResetTimes: number
  TaskInfo: {  [repeated]
    Pos: number
    Count: number
    Status: number
  }

-- === s_team_quick_chat_edit ===
  OpCode: number
  Index: number
  Msg: string

-- === c_usj_enter_next_zone ===
  CurrentZoneId: number
  CurrentPointId: number

-- === s_teach_pvp_info ===

-- === c_act_hero_task_info ===
  ActId: number
  TaskList: {  [repeated]
    Id: number
    Value: number
    State: byte
    ExtValue: number
    ExtState: byte
  }

-- === s_card_fame_lvup ===
  CardUid: number
  ItemList: {  [repeated]
    ItemId: number
    Amount: number
  }
  FameLv: dword
  FameExp: number

-- === c_mail_get_info ===
  mpMailInfo: mail_info

-- === s_client_error ===
  Msg: string

-- === s_league_pvp_horn ===
  ResourceId: number
  Type: number

-- === c_league_board_oper_info ===
  LeagueId: number
  BoardId: number
  SupportList: {  [repeated]
    Uid: number
    Name: string
    AvatarId: byte
    AvatarFrameId: byte
    Level: number
    IsOut: number
  }
  OpposeList: {  [repeated]
    Uid: number
    Name: string
    AvatarId: byte
    AvatarFrameId: byte
    Level: number
    IsOut: number
  }

-- === s_peak_battle_bet ===
  UidList: number [repeated]

-- === s_league_pvp_max_hp ===
  Uid: number
  MaxHp: number

-- === c_frame_md_check ===
  Uid: number
  CurFrame: number
  Md5: string

-- === c_title_sync ===
  Id: number
  State: byte
  EndTime: number

-- === c_area_event_login_data ===
  StageData: area_event_stage_data [repeated]
  DiffStageData: area_event_stage_data [repeated]
  CacheStageId: number
  DifficultCacheStageId: number
  NormalLineup: number [repeated]
  ActLineup: number [repeated]
  DiffLineup: number [repeated]
  StageFightTimes: area_event_stage_times [repeated]
  DiffStageFightTimes: area_event_stage_times [repeated]

-- === s_area_event_wipe ===
  AreaEventId: number

-- === s_act_boss_challenge_over ===
  Damage: number

-- === c_league_money_log ===
  LeagueId: number
  LeagueMoneyLogNo: number
  LeagueMoneyLogs: {  [repeated]
    iMoneyLogId: number
    arrArgs: string [repeated]
    iMoneyLogTime: number
    iMoneyLogNo: number
  }

-- === s_activity_shop_buy ===
  GoodsID: number
  Num: number

-- === s_gem_on ===
  UUid: number
  HeroCId: number
  SkillId: number
  Pos: number

-- === c_hero_rank_attr ===
  AttrList: {  [repeated]
    Id: string
    Value: number
  }

-- === s_chaos_match_cancel ===

-- === s_fenshen_daily_reward ===

-- === s_userinfo_birthday ===
  Year: number
  Month: byte
  Day: byte

-- === c_league_get_rank_simple_info ===
  RankSimpleInfo: {  [repeated]
    LeagueId: number
    LeagueName: string
    HeadIcon: number
    HeadFrameIcon: number
    WeekGongXun: number
  }

-- === c_item_limit_count ===
  CountList: {  [repeated]
    ItemId: number
    Count: number
  }

-- === s_login_drama_finish ===
  Uid: number
  StageId: number

-- === s_group_play_sync ===
  LoadValue: number

-- === s_card_resonance ===
  Uid: number
  PieceId: number [repeated]

-- === c_league_pvp_is_bye ===
  LeagueId: number
  OverScore: number
  AddScore: number

-- === c_home_clean ===
  Uid: number

-- === s_league_modify_audit ===
  LeagueId: number
  Status: byte
  Lv: byte
  Achieve: number

-- === c_offlinepvp_buy ===
  Times: number

-- === c_share_make_up ===
  Id: number

-- === s_task_get_tasklist_bytype ===
  task_type: number

-- === s_battlefield_get_reward ===

-- === s_fenshen_aid_panel ===

-- === c_friend_update_int ===
  Uid: number
  Infos: {  [repeated]
    Key: byte
    Value: number
  }

-- === c_card_active_hole ===
  CardUid: number
  HoleId: number
  IsSuccess: number

-- === s_campaign_trigger_interact ===
  FieldId: number
  AreaId: number

-- === s_rogue_pass_start ===
  PassId: number

-- === s_group_back_channel ===
  ActiveQuit: number

-- === c_equip_remould ===
  EquipPos: byte
  RemouldLv: byte
  RemouldProgress: dword
  Crit: byte

-- === c_team_out_team ===
  Uid: number
  Name: string

-- === s_equip_breakthrough ===
  EquipPos: byte
  BreakLv: byte

-- === c_league_pvp_view_fight ===
  FightList: {  [repeated]
    Uid: number
    Fight: number
  }

-- === c_league_invite_info ===
  InviterUid: number
  InviterName: string
  LeagueId: number
  LeagueName: string
  LeagueLv: word
  LeagueMemberAmount: word
  LeagueHeadIcon: number
  LeagueHeadFrameIcon: number
  LeagueAd: string

-- === c_league_change_icon ===
  LeagueId: number
  HeadIcon: number
  HeadFrameIcon: number

-- === c_attached_card_book ===
  Page: number
  Book: {  [repeated]
    ItemId: number
    Type: byte
  }

-- === c_crosspvp_set_pos ===
  TbPos: crosspvp_pos [repeated]

-- === c_toplist_one ===
  List: {  [repeated]
    ID: byte
    SubName: number
    RankInfo: top_rank_data
    IsCross: number
  }

-- === c_league_appoint ===
  LeagueId: number
  JobInfo: {  [repeated]
    MemberUid: number
    Job: byte
  }

-- === c_list_reward ===
  RewardList: stage_reward [repeated]

-- === c_battlefield_pk_receive ===
  Uid: number
  Name: string
  Time: number

-- === c_stage_playback ===
  StageUid: number
  CurGroup: number
  TotalGroup: number
  TotalFrame: number
  RelayList: {  [repeated]
    FrameId: number
    ProtoType: byte
    Data: string
    FrameData: {  [repeated]
      Cmd: number [repeated]
    }
  }

-- === c_strength_info ===
  BuyTimes: number

-- === c_team_punish ===
  PunishTime: number

-- === s_campaign_drama_index_add ===
  DramaIndex: number

-- === c_interaction_config_exchange ===
  Type: byte
  SrcIndex: number
  DstIndex: number
  HeroId: number
  Result: byte

-- === s_friend_delapply ===
  TargetUid: number

-- === c_attached_card_info ===
  AttachedCardInfo: {  [repeated]
    HeroId: number
    SlotInfo: {  [repeated]
      Index: number
      ACardUid: number
    }
  }

-- === s_league_list_info ===
  LeagueId: number

-- === c_recharge_reward_info ===
  Once: {  [repeated]
    Id: number
    State: byte
  }
  Total: {  [repeated]
    Id: number
    State: byte
  }

-- === s_act_lang_info ===
  ActId: number
  LangType: string

-- === c_scene_enter ===
  SceneUid: number
  X: number
  Y: number
  Z: number
  SceneId: number
  Mode: byte
  EnterMode: byte
  Climbing: climbing
  Extra: {  [repeated]
    Key: string
    Value: number
  }

-- === c_league_pvp_resource_occupy ===
  ResourceId: number
  OccupyPos: number
  Uid: number
  Camp: number
  Time: number

-- === s_mail_get_list ===
  iVersion: number

-- === c_group_team_invite_list ===
  InviteList: group_invite_info [repeated]

-- === s_welfare_total_login ===
  Id: number

-- === c_group_team_leave ===
  GroupId: number
  Uid: number

-- === c_crosspvp_note ===
  AtkNotes: {  [repeated]
    IsAtk: byte
    Result: byte
    OldPoint: number
    NewPoint: number
    FaceIcon: dword
    FaceFrame: dword
    Name: string
    Fighting: number
    Time: number
    RankId: number
    HostId: dword
  }
  DefNotes: {  [repeated]
    IsAtk: byte
    Result: byte
    OldPoint: number
    NewPoint: number
    FaceIcon: dword
    FaceFrame: dword
    Name: string
    Fighting: number
    Time: number
    RankId: number
    HostId: dword
  }

-- === c_usj_end_stage ===
  CurrentZoneId: number
  CurrentPointId: number
  CurrentHeroUid: number
  UserTotalScore: number
  PointReward: {  [repeated]
    PointId: number
    RewardState: byte
  }
  UseTime: number
  HurtSum: number
  Score: number
  HightestScore: number
  Reason: byte
  HpPercent: number
  BaseScore: number
  TimeScore: number

-- === c_equip_list ===
  UidList: number [repeated]

-- === c_login_account_info ===
  URS: string
  Uid: number
  DramaFlag: byte
  DramaStep: byte
  RoleList: {  [repeated]
    Uid: number
  }
  IsNewAccount: byte

-- === s_userinfo_sex_hide ===
  Hide: byte

-- === s_stage_play_sync ===
  SyncData: {  [repeated]
    Key: string
    Val: number
  }

-- === s_guide_drama ===
  Uid: number
  Id: number
  Step: number
  skip: number

-- === c_battlefield_task_add ===
  Tasks: battlefield_task

-- === c_area_event_info ===
  StageData: area_event_stage_data

-- === c_chaos_fight_record ===
  Records: {  [repeated]
    IsWin: number
    Kill: number
    Dead: number
    Score: number
    Time: number
    MatchType: number
    IsCardReset: number
    IsPassive: number
  }

-- === c_title_info ===
  List: {  [repeated]
    Id: number
    State: byte
    EndTime: number
  }

-- === c_group_member_change ===
  MembersData: group_member_data

-- === c_peak_battle_group_rival_info ===
  RivalInfo: {  [repeated]
    HostId: number
    Uid: number
    Name: string
    ChooseHeroList: number [repeated]
    Fight: number
    WinCount: number
  }

-- === c_usj_cycle_id ===
  CycleId: number

-- === c_league_pvp_tips ===
  SelfTips: league_pvp_tips
  RivalTips: league_pvp_tips

-- === c_team_quick_chat_edit ===
  OpCode: number
  Index: number
  Msg: string

-- === s_attached_card_oper ===
  HeroId: number
  Index: number
  Oper: number
  ACardUid: number

-- === c_battlefield_task_replace ===
  Index: byte

-- === s_pay_bonus ===
  Level: number

-- === s_relax_stage_get_box ===

-- === c_teach_info ===
  HeroInfo: {  [repeated]
    HeroCId: number
    SkillList: {  [repeated]
      SkillId: number
      Count: number
    }
  }

-- === c_card_new ===
  Uid: number

-- === c_act_monopoly_info ===
  ActId: number
  CurIndex: number
  EffectList: {  [repeated]
    EffectId: number
    Params: number [repeated]
  }
  DramaStatus: byte
  TotalDiceNum: number

-- === c_flipcard_list ===
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === s_battlefield_real_enter_pvp ===
  Type: number
  OneUid: number
  OtherUid: number

-- === s_fenshen_start ===

-- === c_item_deduct ===
  ItemList: normal_item_info [repeated]

-- === s_league_pvp_status ===

-- === s_league_tech_join ===
  LeagueId: number
  WeekTechId: number
  HeroClass: number

-- === s_peak_battle_ban_hero ===
  HeroCIdList: number [repeated]

-- === c_home_clean_info ===
  CleanList: number [repeated]

-- === c_avatar_use ===
  Id: number

-- === s_pressure_stage_detail ===
  StageId: number

-- === c_friend_send_strength_notify ===
  TargetUid: number

-- === s_entrust_task_get_reward ===
  TaskUniqId: number

-- === s_server_frame ===
  CmdData: number [repeated]

-- === s_league_pvp_view_declaration ===

-- === c_act_exercise_update ===
  ActId: number
  StageList: {
    Id: number
    State: byte
    StartTime: number
    RewardList: {  [repeated]
      ItemId: number
      Count: number
      IsSuper: byte
    }
    HeroList: {  [repeated]
      Index: number
      HeroCId: number
    }
  }

-- === s_night_fight_fight_over ===
  StageId: number
  IsWin: number

-- === c_act_jump_sync_act_info ===
  DailyStatus: number
  DailyMaxScore: number
  IsEgg: number
  CondStatus: {  [repeated]
    Id: number
    Count: number
    Status: number
  }

-- === s_attached_card_enhance ===
  TargetUid: number
  FeedUids: number [repeated]

-- === s_strength_buy ===
  CurGold: number

-- === c_home_role_event_list ===
  Data: home_role_event [repeated]

-- === c_home_checkin ===
  RoleId: number

-- === c_area_event_switch_hero ===
  ControlId: number

-- === c_equip_material_merge_to ===
  MergeStatus: byte

-- === c_cov_code_dump ===
  state: number
  str: string

-- === c_team_member_attr ===
  UserUid: number
  AttrName: string [repeated]
  Value: number [repeated]
  AttrNameStr: string [repeated]
  ValueStr: string [repeated]
  ExtraIndex: number [repeated]
  ExtraVal: number [repeated]

-- === c_stage_extra_reward ===
  UserUid: number
  DrawItems: item_data [repeated]

-- === c_gem_update ===
  item: special_item_info

-- === c_act_eye_sight_map ===
  Id: byte
  Map: byte [repeated]

-- === s_equip_merge_to ===
  EquipUidList: number [repeated]

-- === c_group_base_data ===
  Id: number
  Difficult: number

-- === c_zhanling_get_reward ===
  ActId: number
  Id: number
  RewardType: byte

-- === s_act_sport_race_report ===
  ActId: number
  Id: number
  Result: byte

-- === c_league_pvp_status ===
  Status: number

-- === s_group_team_invite_list ===

-- === s_act_winding_request_toplist ===
  WindId: number
  UpdateTime: number

-- === c_secret_out_key ===

-- === c_act_mini_game_update ===
  ActId: number
  StageList: {  [repeated]
    Id: number
    State: byte
  }
  BoxList: {  [repeated]
    Id: number
    Count: number
  }

-- === c_running_feedback ===
  ID: number
  Params: {  [repeated]
    Type: number
    Value: string [repeated]
  }

-- === s_offlinepvp_task ===

-- === s_league_kick ===
  LeagueId: number
  TargetUid: number

-- === s_recharge_reward_first_get ===
  Round: number
  Day: number

-- === c_battlefield_hallinfo ===
  StartId: number
  Infos: {  [repeated]
    Uid: number
    Name: string
    FaceIcon: string
    Score: number
    FightCount: number
    WinRate: number
    UseMercenaryId: number
  }

-- === c_teach_pvp_info ===
  GuideId: number

-- === s_league_list ===

-- === s_act_allsvr_stage_boss ===
  ActId: number
  BossId: number
  Diffcult: number
  Cid: number
  BuffList: number [repeated]

-- === s_team_ready ===
  IsReady: number

-- === s_fashion_oper ===
  Id: number
  Type: byte

-- === c_achieve_open_end ===

-- === s_base_station_all_info ===
  iClientVersion: number

-- === c_card_fame_lvup ===
  CardUid: number
  IsSucc: byte

-- === c_league_pvp_update_report ===
  Reports: league_pvp_report [repeated]

-- === s_shot_finish ===
  Point: number
  TartgetList: number [repeated]

-- === s_usj_get_zone_reward ===
  ZoneId: number
  RewardType: number

-- === c_group_team_choose_list ===
  GroupId: number
  ChooseList: group_member_base_info [repeated]

-- === c_egg_task_update ===
  ETasks: egginfo

-- === s_teach_pvp ===
  GuideId: number

-- === c_chaos_record_detail ===
  RecordId: number
  WinCamp: number
  Info: {  [repeated]
    Uid: number
    Name: string
    Camp: number
    AvatarId: number
    AvatarFrameId: number
    HeroId: number
    Kill: number
    Death: number
    ComboKill: number
    TotalHurt: number
    HurtRate: number
  }

-- === s_league_board_oper_info ===
  LeagueId: number
  BoardId: number

-- === c_rogue_chg_record_name ===
  Index: number
  HeroIndex: number
  Name: string

-- === s_mail_quickly_get_attach ===

-- === s_rogue_info ===

-- === c_chaos_choose_hero ===
  HeroClassId: number
  Result: number

-- === s_friend_recive_strength ===
  TargetUid: number

-- === c_user_change_int ===
  key: number
  value: number

-- === c_pressure_info ===
  Type: number
  Cycle: byte
  Score: number
  Rank: number
  UserCount: number
  Count: byte
  HeroFight: number
  HeroList: {  [repeated]
    HeroId: number
    Power: number
  }
  TaskList: {  [repeated]
    TaskId: number
    State: byte
  }
  StageList: {  [repeated]
    StageId: number
    Score: number
  }
  ZanList: number [repeated]

-- === s_secret_area_jump_key ===

-- === c_league_red_point_value ===
  RedPointValue: number
  IsUpdate: byte

-- === s_frame_report ===
  Uid: number
  DataMax: byte
  DataIndex: byte
  CFrame: number
  ReportList: {  [repeated]
    AtrType: byte
    value: number [repeated]
    extval: string [repeated]
  }

-- === c_entrust_task_list ===
  Version: number
  EntrustTaskData: entrust_task_data [repeated]

-- === s_secret_area_cycle_reward ===

-- === c_league_pvp_enter_stage_success ===
  Uids: number [repeated]

-- === s_scene_action_change ===
  ActionId: number

-- === c_league_pvp_horn ===
  ResourceId: number
  Type: number
  UserInfo: league_pvp_fight_data

-- === s_login_player_del ===
  Uid: number

-- === s_card_support_skill ===
  HeroCId: number
  Index: number
  SupportHeroCId: number

-- === c_softball_sync ===
  BestRange: number
  LastRange: number
  BestRank: number
  ThrowChance: number
  Weather: number
  Wind: number

-- === s_team_sync_info ===
  type: number
  NumInfo: number [repeated]
  StrInfo: string [repeated]

-- === s_team_kick_out ===
  TargetUid: number

-- === c_chat_frame_use ===
  Id: number

-- === s_home_guide_task_reward ===
  TaskId: number

-- === s_shop_sell_equip ===
  SellList: number [repeated]

-- === c_friend_apply ===
  Info: {
    HostId: number
    Uid: number
    Name: string
    Level: number
    TopLevel: number
    FaceIcon: number
    FaceFrame: number
    OnLine: number
    Msg: string
    LeaveTime: number
    Time: dword
  }

-- === c_home_guide_task ===
  TaskStatus: home_proof_task_status [repeated]

-- === c_team_search_multi ===
  List: {  [repeated]
    PlayId: number
    SearchList: team_search_info [repeated]
  }
  IsAuto: byte

-- === c_frame_correct_do ===
  CFrame: number
  Data: {  [repeated]
    AtrType: byte
    Uid: number
    Id: number
    Value: number [repeated]
    EString: string [repeated]
  }

-- === s_rogue_pass_exit ===

-- === s_frame_monster_data ===
  monster_data: {  [repeated]
    Uid: number
    Type: byte
    X: number
    Y: number
    BoxFullMode: byte
    OwnerUid: number
    CurFrame: number
    CurAni: string
    CurAniTime: dword
    CurAnimationIdx: number
    State: byte
    BodyBlock: byte
    ReplaceRunAni: string
    Camp: number
    RotationY: number
    SkillId: number
    Info: {
      Id: number
      Face: word
      ShapeVer: number
      MissionLv: number
      StartAnim: string
      DropList: number [repeated]
      MoneyList: number [repeated]
      Alias: string
      GroupId: number
      BallId: number
      AreaId: number
      WallNormal: number [repeated]
      Level: number
      BTParam: string [repeated]
      bNotAsync: byte
    }
  }

-- === s_group_team_invite_done ===
  GroupId: number
  Result: byte

-- === s_title_info ===

-- === s_rogue_endless_phase ===
  phase: number

-- === c_funcopen_query ===
  TargetUid: number
  OpenId: byte
  Result: byte

-- === s_gem_lock ===
  UUid: number
  IsLock: byte

-- === s_group_team_apply_list ===
  GroupId: number

-- === c_shop_info ===
  shopinfo: {  [repeated]
    ShopId: number
    RefreshTime: number
    RefreshCount: number
    Goods: {  [repeated]
      GoodsId: number
      ItemId: number
      Amount: number
      Price: number [repeated]
      PriceType: number
      Discount: number [repeated]
      BuyTimes: number
      NumberList: number [repeated]
    }
  }

-- === c_fenshen_start_panel ===
  ActiveID: number
  FirstLogin: byte
  DailyRewardStatus: byte
  Times: byte

-- === c_base_station_red_point ===
  arrBaseStationIds: byte [repeated]

-- === c_act_consume_get ===
  ActId: number
  Id: number

-- === s_team_set ===
  Lv: number
  Message: string
  SearcLv: number
  TotalScore: number

-- === c_userinfo_sign ===
  Sign: string

-- === s_home_ramble ===

-- === c_team_search ===
  PlayId: number
  SearchList: team_search_info [repeated]
  IsAuto: byte

-- === c_item_sell ===

-- === c_userinfo_tag_get ===
  Id: byte

-- === s_chat_public ===
  channel: byte
  msg: string
  item_links: string
  extdata: string

-- === s_task_accept ===
  task_id: number

-- === s_peak_battle_primary_info ===
  Season: number

-- === c_offlinepvp_note ===
  NoteList: {  [repeated]
    Uid: number
    IsWin: byte
    AtkOrDef: byte
    RankId: number
    RankChange: number
    Time: number
    SelfFighting: number
    RivalFighting: number
  }
  LastCheckTime: number

-- === s_group_team_friend_list ===
  GroupId: number

-- === c_top_level_info ===
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === s_group_goto_channel ===
  GroupId: number
  ChannelId: number

-- === s_herochip_stage_enter ===
  Id: number
  HeroUid: number

-- === s_skill_get_spec_level ===
  HeroUid: number

-- === s_top_level_get ===
  Id: byte

-- === s_act_team_invite ===
  Uid: number

-- === s_usj_task ===

-- === s_crosspvp_rank_reward ===
  RankId: number

-- === c_league_pvp_self_hero_list ===
  HeroList: {  [repeated]
    HeroCId: number
    Hp: number
    BuffLayer: number
    CdTime: number
  }

-- === c_act_exchange ===
  ActId: number
  ExchangeId: number
  ExchangeItem: number

-- === s_stage_quick_reborn ===
  RebornCount: number

-- === s_business_extend_report_reward ===

-- === s_night_fight_info ===

-- === s_interaction_do ===
  Type: byte
  Index: number
  Uid: number

-- === c_league_apply_list ===
  LeagueId: number
  ApplyList: {  [repeated]
    Uid: number
    HeadIcon: number
    HeadFrameIcon: number
    Name: string
    Lv: word
    TopLv: number
    Achieve: number
  }

-- === c_act_empty_shop_info ===
  ActId: number
  MaxPassStage: number

-- === s_rune_overload ===
  HeroCid: word
  Index: byte
  NowLv: word

-- === c_peak_battle_primary_reset_cd ===

-- === s_group_team_invite ===
  iType: byte
  GroupId: number
  TargetUid: number

-- === c_area_event_trigger_change ===
  EventRound: number
  TriggerOnMap: number [repeated]

-- === c_training_info ===
  HeroData: {  [repeated]
    HeroCId: number
    FinishList: number [repeated]
    GetList: number [repeated]
  }

-- === c_top_broadcast_info ===
  Type: string
  EndTime: number

-- === s_crosspvp_rank_info ===

-- === c_pressure_message ===
  Success: byte
  Message: string

-- === c_admission_manual_get_reward ===
  Id: word
  Count: number
  Status: byte

-- === s_campaign_shop_info ===
  FieldId: number
  AreaId: number
  ShopId: number

-- === c_peak_battle_support_info ===
  UserList: peak_battle_data [repeated]
  SupportList: number [repeated]

-- === s_team_search_multi ===
  PlayId: number [repeated]
  Extra: number [repeated]
  IsAuto: byte

-- === c_comment_reply ===
  ReplyInfo: replyinfo

-- === c_scene_sync_int ===
  Uid: number
  KeyValue: number [repeated]

-- === c_peak_battle_wonder_play ===
  BattleType: number
  CurPage: number
  TotalPage: number
  Logs: {  [repeated]
    FightType: number
    Bit: byte
    WinUid: number
    Time: number
    PlayId: number
    LogData: peak_battle_log [repeated]
  }

-- === c_area_event_kick_out ===

-- === c_act_return_info ===
  BounsList: {  [repeated]
    Id: number
    Count: number
  }
  GoodsList: {  [repeated]
    Id: number
    Count: number
  }

-- === c_rogue_endless_fight ===
  HeroIndex: number
  Index: number

-- === c_stage_frame_report ===

-- === s_secret_area_task ===

-- === c_league_modify_audit ===
  LeagueId: number
  Status: byte
  Lv: byte
  Achieve: number

-- === c_peak_attr ===
  Uid: number
  StageId: number
  infos: attribute_string_info [repeated]

-- === c_home_checkin_list ===
  CheckinList: home_checkin_list [repeated]

-- === s_log_point_report ===
  ActId: number
  PointId: number
  CreateTime: number

-- === c_egg_sync ===
  EType: number
  CondType: string
  ParamList: string [repeated]

-- === c_async_cfg_end ===
  NoList: {  [repeated]
    AsyncId: byte
    Key: number
  }
  SameList: {  [repeated]
    AsyncId: byte
    Key: number
  }

-- === s_league_modify_notic ===
  LeagueId: number
  Notic: string

-- === c_crosspvp_info ===
  Season: number
  Point: number
  Rank: number
  SerRank: number
  FightWin: number
  FightCount: number
  TbPos: crosspvp_pos [repeated]
  Challenge: word
  ChanceBuy: word
  STime: number
  ETime: number
  State: word
  BestRankId: word
  RankId: word
  NewSeason: byte

-- === c_group_area_change ===
  AreaId: number
  Index: number
  TransTime: number

-- === s_act_rescue_pass ===
  Id: byte
  Point: number

-- === c_act_task_info ===
  ActId: number
  TaskList: {  [repeated]
    Day: byte
    TaskIdList: number [repeated]
  }

-- === c_act_goods_info ===
  ActId: number
  GoodsList: {  [repeated]
    Id: number
    Count: number
  }

-- === c_peak_battle_status ===
  StartSeason: number
  Season: number
  PeakStatus: number
  StatusSwitchTime: number
  IsOver: byte
  FirstSeTime: number

-- === s_activity_login_push ===

-- === c_shop_buy ===
  IsReturn: byte
  ItemInfo: {  [repeated]
    ItemId: number
    Amount: number
    Uid: number
  }
  ShopId: number
  GoodsId: number
  BuyTimes: number

-- === c_secret_area_task ===
  TaskList: {  [repeated]
    Id: number
    Status: number
    CurValue: number
  }

-- === c_scene_previous_info ===
  SceneId: number
  X: ?
  Y: number
  Z: number

-- === c_friend_quick_recive_strength ===
  TargetUids: number [repeated]

-- === s_title_set ===
  Id: number

-- === s_pressure_hero_fight ===
  StageId: number
  HeroUid: number

-- === s_card_active_hole ===
  CardUid: number
  HoleId: number

-- === s_stage_is_back ===
  StageId: number
  IsBack: byte

-- === c_data_merge_to ===
  str: string

-- === s_stage_leave ===
  StageId: number

-- === c_recharge_reward_first_info ===
  Round: {  [repeated]
    State: byte [repeated]
    GetTime: number
  }

-- === c_recharge_reward_total_update ===
  List: {  [repeated]
    Id: number
    State: byte
  }

-- === s_usj_get_point_reward ===
  ZoneId: number
  PointList: number [repeated]

-- === c_scene_player_info ===
  Uid: number
  Camp: number
  Name: string
  Level: number
  TopLevel: number
  ShowHeroId: number
  LeagueId: number
  LeagueName: string
  TitleId: number
  MoodId: number
  Version: number

-- === c_home_change_name ===
  Floor: number
  Name: string

-- === c_tsssdk_anti ===
  Data: string

-- === s_league_tech_shop_panel ===
  LeagueId: number

-- === s_group_team_leave ===
  GroupId: number

-- === s_usj_get_score_reward ===
  Id: number

-- === s_pressure_stage_finish ===
  StageId: number
  HeroUid: number
  Score: number
  ScoreDetails: number [repeated]
  Save: byte

-- === s_team_new ===
  PlayId: number

-- === c_world_task_reward_rate ===
  Rate: number

-- === c_time_type_sync ===
  Type: number [repeated]
  Time: number [repeated]

-- === c_battlefield_get_reward ===

-- === c_night_fight_sync_status ===
  StageId: number
  StageList: {  [repeated]
    StageId: number
    StageType: number
    StageStatus: number
    HasExtraReward: number
  }
  HeroStatus: {  [repeated]
    HeroUid: number
    TiredValue: number
  }

-- === c_office_herostep_reward ===
  OldHeroStep: number
  HeroStep: number
  Reward: stage_reward [repeated]

-- === c_scene_sync_str ===
  UserUid: number
  Key: number [repeated]
  Value: string [repeated]

-- === c_league_list ===
  LeagueList: {  [repeated]
    LeagueId: number
    Name: string
    HeadIcon: number
    HeadFrameIcon: number
    Lv: byte
    WeekGongXun: number
    MemberAmount: word
  }

-- === s_area_event_leave_stage ===
  LeaveType: number

-- === c_team_match_cancel ===

-- === s_skill_spec_level_up ===
  HeroUid: number
  SpecId: number

-- === s_offline_cache_info ===
  List: {  [repeated]
    Uid: number
  }

-- === c_egg_task_del ===
  EType: number [repeated]

-- === s_crosspvp_info ===

-- === c_scene_move ===
  Uid: number
  Path: {  [repeated]
    X: number
    Y: number
    Z: number
    Face: number
    Speed: number
    ChState: number
    ChAction: byte
    Extra: number
  }

-- === s_stage_frame_report ===

-- === c_office_pick_step ===
  Index: number

-- === c_rogue_bp_info ===
  Lv: byte
  Exp: number
  Reward: byte
  PayRewardLv: byte
  IsHeroLicense: byte
  CurWeekExp: word
  GoodsHaveBrought: {  [repeated]
    Id: number
    Num: number
  }

-- === c_mail_delete ===
  arrMailIds: number [repeated]

-- === s_friend_find ===
  Name: string

-- === s_training_get_reward ===
  HeroCId: number
  SkillId: number

-- === c_platform_access_friend_share ===
  DailyRewardStatus: byte
  TotalShareDays: word

-- === s_rogue_pass_difficult ===
  Difficult: number

-- === s_equip_material_merge_auto ===
  FromItemId: number
  ToItemId: number
  Count: number

-- === s_hero_rank_stage_enter ===
  StageId: number

-- === s_userinfo_other ===
  Uid: number

-- === c_equip_dieset_enhance ===
  EquipPos: byte
  DiesetIndex: byte
  DiesetProgress: dword
  Crit: byte

-- === c_resource_stage_info ===
  Progress: {  [repeated]
    Type: number
    Level: number
  }
  HeroUid: number
  PassStage: number [repeated]
  Chances: {  [repeated]
    Type: number
    Chances: number
  }

-- === c_attached_card_lv ===
  TargetUid: number
  Lv: number
  Exp: number

-- === c_offlinepvp_array ===
  AtkPos: offlinepvp_hero_pos [repeated]
  DefPos: offlinepvp_hero_pos [repeated]

-- === c_league_board_comment_list ===
  LeagueId: number
  BoardId: number
  CommentList: {  [repeated]
    ParentId: number
    CommentId: number
    IsDel: byte
    Msg: string
    Time: number
    SenderInfo: {
      Uid: number
      Name: string
      AvatarId: byte
      AvatarFrameId: byte
    }
  }

-- === c_platform_access_friend_share_reward ===
  RewardId: number

-- === c_league_tech_buy_week ===
  LeagueId: number
  WeekTechId: number
  JoinCount: byte
  Progress: number
  Time: number
  EventList: {  [repeated]
    EventId: number
    CurLeagueLv: byte
    StartTime: dword
    EndTime: dword
    DealTimes: byte
    IsReward: byte
  }

-- === c_login_player_del ===
  Uid: number

-- === s_task_enter_stage ===
  IsEnter: byte
  x: number
  y: number

-- === s_act_seven_day_buy ===
  ActId: number
  GoodsId: number

-- === c_group_display_boss ===

-- === s_office_info ===

-- === c_usj_task_update ===
  TaskList: {  [repeated]
    Id: number
    Status: byte
    CurValue: number
  }

-- === s_item_lock ===
  ItemUid: number
  IsLock: byte

-- === s_act_consume_get ===
  ActId: number
  Id: number

-- === c_welfare_strength_supply ===
  Id: number
  List: number [repeated]

-- === c_usj_get_zone_reward ===
  ZoneId: number
  RewardType: number

-- === s_growth_fund_reward ===
  Id: number

-- === s_grid_box_info ===
  ActId: number

-- === c_stage_damage_info ===

-- === c_ping_fight_list ===

-- === c_card_combat_force ===
  UpdateList: {  [repeated]
    CardUid: number
    CombatForce: number
  }

-- === c_toplist_page ===
  ID: byte
  SubName: number
  CurPageNum: number
  MaxPageNum: number
  Page: top_rank_data [repeated]
  IsCross: number

-- === c_item_special_list ===
  page: number
  totalpage: number
  item: special_item_info [repeated]

-- === c_league_boss_total_damage ===
  LeagueId: number
  BossTime: dword
  TotalDamage: number

-- === c_stage_play_sync ===
  UUid: number
  SyncData: {  [repeated]
    Key: string
    Val: number
  }

-- === c_equip_attr_switch ===
  FromEquipUid: number
  ToEquipUid: number

-- === c_home_role_mood_update ===
  Data: home_role_mood [repeated]

-- === c_pay_check ===
  ShopId: number
  GoodsId: number
  OrderId: string
  CBUrl: string
  Extra: string [repeated]

-- === c_act_baohao_practice_sync_info ===
  CurPoints: number
  ResetTimes: number
  CondInfo: {  [repeated]
    Id: number
    Count: number
    Status: number
  }
  TaskInfo: {  [repeated]
    Pos: number
    TaskID: number
    CompCount: number
    Desc: string
    Goto: number
    Goto2: number
    Points: number
    Title: string
    Type: string
    Rewards: {  [repeated]
    }
    Count: number
    Status: number
  }

-- === s_crosspvp_set_pos ===
  TbPos: {  [repeated]
    FormationId: byte
    Pos: byte
    HeroCId: number
  }

-- === c_achieve_chgstatus ===
  Info: achieveinfo [repeated]

-- === c_secret_area_time_record_update ===
  Tag: string
  TeamUid: number

-- === c_group_team_be_invited ===
  InviteInfo: group_invite_info

-- === c_secret_refuse_key ===
  UserUid: number

-- === c_secret_area_jump_key ===

-- === s_usj_end_stage ===
  EndType: byte
  Reason: byte
  HeroUid: number
  HpPercent: number
  BeHitTimes: number
  HurtSum: number

-- === s_league_tech_modify_notic ===
  LeagueId: number
  TechNotic: string

-- === c_scene_shape_change ===
  Uid: number
  CacheShapeId: number

-- === c_act_daily_stage_result ===
  ActId: number
  Count: {
    Id: number
    Count: number
    Extra: {
      NumList: number [repeated]
      StrList: string [repeated]
    }
  }
  RewardList: {  [repeated]
    AddLog: stage_reward [repeated]
  }

-- === s_pressure_task_reward ===
  TaskType: byte
  TaskId: number

-- === s_act_mini_game_enter ===
  ActId: number
  Id: number

-- === c_scene_hero_change ===
  Uid: number
  ShowHeroId: number
  ShapeCacheId: number

-- === s_theater_open ===

-- === c_business_extend_report_reward ===

-- === s_act_client_trigger ===
  ActId: number
  Id: number

-- === c_rune_overload ===
  HeroCid: word
  Index: byte

-- === s_battlefield_task_update ===
  Index: byte
  TaskId: number
  ProAdd: byte

-- === s_friend_apply ===
  Uid: number
  Msg: string

-- === s_rogue_endless_end ===
  Time: number
  DeadTimes: number
  RoundList: {  [repeated]
    UseTime: number
    HitTimes: number
  }

-- === c_scene_obj_delete ===
  ObjList: number [repeated]

