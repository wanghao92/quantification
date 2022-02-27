-- 创建聚宽的信息表
create table IF NOT EXISTS `security_info`(
    `stock_code` varchar(64) ,
    `display_name` varchar(64) not null comment '中文名称',
    `simple_name` varchar(64) comment '缩写简称',
    `stock_type` varchar(8) not null comment '类型，stock(股票)，index(指数)，etf(ETF基金)，fja（分级A），fjb（分级B），fjm（分级母基金），mmf（场内交易的货币基金）open_fund（开放式基金）, bond_fund（债券基金）, stock_fund（股票型基金）, QDII_fund（QDII 基金）, money_market_fund（场外交易的货币基金）, mixture_fund（混合型基金）, options(期权)',
    `start_date` datetime comment '上市日期',
    `end_date` datetime comment '退市日期，如果没有退市则为2200-01-01',
    primary key (`stock_code`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
