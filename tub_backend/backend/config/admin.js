module.exports = ({ env }) => ({
  auth: {
    secret: env('ADMIN_JWT_SECRET', 'a1a91cd0f050541e34c9e9ffa03a58a8'),
  },
});
