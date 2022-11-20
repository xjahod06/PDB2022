db = db.getSiblingDB('pdb')

db.createUser({
    user: 'user',
    pwd: 'passwd',
    roles: [
        {
            role: 'readWrite',
            db: 'pdb',
        },
    ],
});